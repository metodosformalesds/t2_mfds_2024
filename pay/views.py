from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment as PayPalPayment
from product.models import ShoppingCart, UserAccount, Client, Supplier, SupplierPaymentMethodModel,ClientAddress,OrderItem,Order,Payment, Shipment, HistorialCompras
from django.views.decorators.http import require_POST
from .paypal import paypalrestsdk
from django.db import transaction
from django.http import JsonResponse
from supplier.forms import WithdrawForm
import random
import string
from django.utils import timezone
from django.conf import settings
import requests 
from django.http import JsonResponse, HttpResponse
import stripe
import random
import string
from datetime import timedelta
import logging
from django.utils.timezone import now
from shipping.views import determinar_courier_code
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY_TEST

logger = logging.getLogger(__name__)

def generar_tracking_number():
    """
    Genera un número de seguimiento válido para Ship24.
    """
    prefix = ''.join(random.choices(string.ascii_uppercase, k=2))  # Prefijo con letras mayúsculas
    middle = ''.join(random.choices(string.digits, k=8))  # Ocho dígitos
    suffix = ''.join(random.choices(string.ascii_uppercase, k=2))  # Sufijo con letras mayúsculas
    return f"{prefix}{middle}{suffix}"

def crear_tracker_ship24(tracking_number, courier_code, destination_postcode, shipment_date=None):
    """
    Crea un tracker en Ship24 y retorna el trackerId.
    """
    # Validación y formato de datos
    destination_postcode = str(destination_postcode)  # Convertir a string

    url = "https://api.ship24.com/public/v1/trackers"
    headers = {
        "Authorization": f"Bearer {settings.SHIP24_API_KEY}",
        "Content-Type": "application/json",
    }

    # Usar la fecha proporcionada o la actual
    shipping_date = shipment_date.isoformat() if shipment_date else now().isoformat()

    payload = {
        "trackingNumber": tracking_number,
        "shipmentReference": f"order_{tracking_number}",
        "originCountryCode": "MX",  # Siempre México
        "destinationCountryCode": "MX",  # Siempre México
        "destinationPostCode": destination_postcode,
        "shippingDate": shipping_date,  # Se envía como ISO-8601
        "courierCode": [courier_code],
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 400:
            logger.error(f"Error 400 al crear tracker: {response.json()}")
        response.raise_for_status()

        data = response.json()
        tracker_id = data.get("data", {}).get("tracker", {}).get("trackerId")
        if tracker_id:
            logger.info(f"Tracker creado correctamente en Ship24: {tracker_id}")
            return tracker_id
        else:
            logger.error(f"Error al crear tracker: {data}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al conectar con Ship24: {e}")
        return None
        
def registrar_rastreador_y_envio(order, client, item):
    """
    Registra un rastreador en Ship24 y guarda el trackerId en la base de datos.
    """
    tracking_number = generar_tracking_number()

    # Obtener código postal del cliente
    try:
        address = client.clientaddress_set.first()
        if not address:
            raise ValueError("El cliente no tiene una dirección registrada.")
        destination_postcode = str(address.client_zip_code)  # Convertir ZIP a string
    except Exception as e:
        logger.error(f"Error al obtener la dirección del cliente: {e}")
        destination_postcode = "00000"  # Valor por defecto

    # Crear un nuevo envío en la base de datos con una fecha de envío válida
    shipment_date = timezone.now()  # Fecha de envío actual
    nuevo_envio = Shipment.objects.create(
        order=order,
        shipment_tracking_number=tracking_number,
        shipment_carrier="dhl",  # Cambiar según lógica
        shipment_status="Pendiente",
        shipment_date=shipment_date,  # Fecha actual para evitar errores de NULL
        shipment_estimated_delivery_date=shipment_date + timedelta(days=7),
    )

    # Crear tracker en Ship24
    try:
        tracker_id = crear_tracker_ship24(
            tracking_number=tracking_number,
            courier_code="dhl",
            destination_postcode=destination_postcode,
            shipment_date=shipment_date
        )
        if tracker_id:
            nuevo_envio.tracker_id = tracker_id
            nuevo_envio.save()
            logger.info(f"Tracker creado correctamente para {tracking_number}")
        else:
            logger.error(f"Error creando tracker para {tracking_number}")
    except Exception as e:
        logger.error(f"Error al registrar rastreador: {e}")

@require_POST
def iniciar_pago_stripe(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión para realizar un pago.")
        return redirect("client_login")

    try:
        carrito_items = ShoppingCart.objects.filter(client_id=user_id)
        if not carrito_items.exists():
            messages.error(request, "Tu carrito está vacío.")
            return redirect("cart")

        monto_total = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)
        monto_total_cents = int(monto_total * 100)  # Stripe usa centavos

        # Crear la sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': "Compra de productos",
                        },
                        'unit_amount': monto_total_cents,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('pago_exitoso_stripe')) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse('cart')),
            metadata={
                'user_id': user_id,  # Asociar el ID de usuario
            },
        )

        return redirect(session.url, code=303)
    except Exception as e:
        logger.error(f"Error al crear la sesión de Stripe: {e}")
        messages.error(request, "Error al procesar el pago.")
        return redirect("cart")

def validar_datos_ship24(tracking_number, origin_country, destination_country, destination_postcode):
    """
    Valida los datos requeridos antes de enviarlos a la API de Ship24.
    """
    if not tracking_number or not tracking_number.isalnum():
        raise ValueError("El número de seguimiento debe ser alfanumérico.")
    if len(tracking_number) < 5 or len(tracking_number) > 50:
        raise ValueError("El número de seguimiento debe tener entre 5 y 50 caracteres.")
    if len(origin_country) not in [2, 3] or len(destination_country) not in [2, 3]:
        raise ValueError("Los códigos de país deben ser ISO 3166-1 alpha-2 o alpha-3.")
    if not destination_postcode.isdigit():
        raise ValueError("El código postal debe ser numérico.")
    logger.info("Datos de Ship24 validados correctamente.")

@require_POST
def iniciar_pago_view(request):
    # Obtener el ID del usuario desde la sesión
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "Debes iniciar sesión para realizar un pago.")
        return redirect("client_login")

    # Obtener el UserAccount y luego el Client asociado
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect("cart")

    # Filtrar el carrito del cliente actual
    carrito_items = ShoppingCart.objects.filter(client=client)

    if not carrito_items:
        messages.error(request, "El carrito está vacío. Agrega productos para continuar con el pago.")
        return redirect("cart")

    # Validar que cada producto en el carrito tenga un precio válido
    for item in carrito_items:
        if item.product.product_price <= 0:
            messages.error(request, f"El producto '{item.product.product_name}' tiene un precio inválido.")
            return redirect("cart")

    # Calcular el monto total y formatearlo a dos decimales
    monto_total = '{:.2f}'.format(sum(item.product.product_price * item.cart_product_quantity for item in carrito_items))
    if float(monto_total) == 0:
        messages.error(request, "El monto total no puede ser cero. Verifica los productos en tu carrito.")
        return redirect("cart")

    # Crear el pago en PayPal
    pago = PayPalPayment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse("pago_exitoso")),
            "cancel_url": request.build_absolute_uri(reverse("pago_cancelado")),
        },
        "transactions": [{
            "item_list": {
                "items": [  # Ajusta para agregar cada ítem del carrito
                    {
                        "name": item.product.product_name,
                        "sku": str(item.product.id_product),
                        "price": str(item.product.product_price),
                        "currency": "USD",
                        "quantity": item.cart_product_quantity,
                    } for item in carrito_items
                ]
            },
            "amount": {
                "total": str(monto_total),
                "currency": "USD"
            },
            "description": "Compra de productos de Solid Steel"
        }]
    })

    # Redirigir al usuario a PayPal si el pago fue creado exitosamente
    if pago.create():
        for link in pago.links:
            if link.method == "REDIRECT":
                return redirect(link.href)  # Redirige al usuario a PayPal
    else:
        print("Error al crear el pago en PayPal:", pago.error)  # Detalle del error en consola
        messages.error(request, "Error al crear el pago con PayPal")
        return redirect("cart")  # Redirige de nuevo al carrito en caso de error


def pago_exitoso_view(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Debes iniciar sesión para completar el pago.")
        return redirect("client_login")

    # Ejecutar el pago en PayPal
    try:
        pago = PayPalPayment.find(payment_id)
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist, PayPalPayment.DoesNotExist):
        messages.error(request, "Error procesando el pago o encontrando la información del usuario.")
        return redirect("cart")

    if pago.execute({"payer_id": payer_id}):
        # Pago exitoso
        payment_date = timezone.now()  # Usar la fecha y hora actual
        payment_method = "PayPal"

        # Obtener el ID de la transacción de PayPal
        transaction_id = pago.transactions[0].related_resources[0].sale.id

        # Obtener items del carrito y calcular el total
        carrito_items = ShoppingCart.objects.filter(client=client)
        subtotal = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)
        total = subtotal  # Si tienes impuestos u otros cálculos, ajústalo aquí

        # Crear una nueva orden
        address = ClientAddress.objects.filter(client=client).first()
        order = Order.objects.create(
            client=client,
            address=address,
            order_date=payment_date
        )

        # Crear los items de la orden y actualizar el balance del proveedor
        with transaction.atomic():
            for item in carrito_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.cart_product_quantity,
                    price_at_purchase=item.product.product_price
                )
                supplier = item.product.supplier
                supplier.balance += item.product.product_price * item.cart_product_quantity
                supplier.save()

                # Registrar el envío para cada producto
                registrar_rastreador_y_envio(order, client, item)

        # Crear el registro del pago con los detalles correctos
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            payment_amount=total,
            payment_status="Exitosa",
            app_user=client,
            payment_bool=True,
            stripe_checkout_id=payment_id
        )

        # Limpiar el carrito del usuario
        ShoppingCart.objects.filter(client=client).delete()

        # Pasar los datos al contexto para mostrarlos en la plantilla
        return render(request, 'cart/success.html', {
            'transaction_id': transaction_id,
            'payment_date': payment_date,
            'payment_method': payment_method,
            'subtotal': f"{subtotal:.2f}",  # Formatear a dos decimales
            'total': f"{total:.2f}",  # Formatear a dos decimales
            'status': "Exitosa"
        })
    else:
        # Error en el pago
        messages.error(request, "Error al confirmar el pago.")
        return redirect("cart/error") #bien

def pago_cancelado_view(request):
    messages.info(request, "El pago fue cancelado.")
    return redirect("cart")


def mostrar_pagos_view(request):
    # Opcional: calcula el monto total o realiza cualquier operación necesaria
    user_id = request.session.get('user_id')
    carrito_items = ShoppingCart.objects.filter(client_id=user_id)
    monto_total = sum(item.product.price * item.cart_product_quantity for item in carrito_items)

    return render(request, "pagos.html", {"monto_total": monto_total})


def escojer_metodo_view(request):
    return render(request, "opcion_pago.html")

def generar_id_unico():
    """
    Genera un identificador único compuesto de 12 caracteres alfanuméricos.

    Returns:
        str: Un identificador único con letras y números aleatorios.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def create_payout(request):
    """
    Vista que permite a un proveedor retirar dinero de su balance mediante PayPal.
    
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el método de solicitud es POST.
        2. Valida el formulario `WithdrawForm` para obtener la cantidad a retirar.
        3. Recupera el proveedor autenticado mediante la sesión.
        4. Verifica si el balance del proveedor es suficiente para la cantidad solicitada.
        5. Descuenta la cantidad del balance del proveedor y guarda el cambio.
        6. Genera IDs únicos para `sender_batch_id` y `sender_item_id`.
        7. Configura y realiza el pago usando PayPal API.
        8. Si el pago es exitoso, muestra un mensaje de éxito; de lo contrario, muestra un mensaje de error.

    Returns:
        HttpResponse: Redirige a la página de retiro de saldo con un mensaje de éxito o error.

    Manejo de errores:
        - Si el formulario no es válido, redirige con un mensaje de error.
        - Si la solicitud no es POST, redirige con un mensaje de error.
        - Si ocurre un error en el payout de PayPal, redirige con un mensaje de error.

    Dependencias:
        - `random`: Para generar IDs aleatorios.
        - `paypalrestsdk`: Para interactuar con la API de PayPal.
        - `Supplier`: Modelo que representa al proveedor.
        - `SupplierPaymentMethodModel`: Modelo que almacena los métodos de pago del proveedor.
        - `WithdrawForm`: Formulario utilizado para solicitar el retiro.
        - `UserAccount`: Modelo que representa las cuentas de usuario.
        - `messages`: Para mostrar mensajes flash al usuario.

    Contexto adicional:
        - La función asume que el proveedor está autenticado y su ID está almacenado en la sesión (`supplier_id`).

    Ejemplo de uso:
        - El proveedor completa el formulario de retiro y envía la solicitud.
        - Si el balance es suficiente, se realiza un pago mediante PayPal y se actualiza el balance del proveedor.
    """
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():
            cantidad_retirar = form.cleaned_data['cantidad']

            user_id = request.session.get('supplier_id')
            user = get_object_or_404(UserAccount, pk=user_id)
            supplier = get_object_or_404(Supplier, user=user)

            cantidad_retirar = float(cantidad_retirar)

            # Verifica si el balance es suficiente
            if cantidad_retirar > supplier.balance:
                messages.error(request, "Saldo insuficiente para retirar esta cantidad.")
                return redirect("retirar_saldo")

            # Descuenta la cantidad del balance
            supplier.balance -= cantidad_retirar
            supplier.save()

            # Genera IDs aleatorios para sender_batch_id y sender_item_id
            sender_batch_id = generar_id_unico()
            sender_item_id = generar_id_unico()

            # Configura el payout
            payment_method = get_object_or_404(SupplierPaymentMethodModel, supplier=supplier)
            supplier_email = payment_method.supplier_payment_email
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": sender_batch_id,
                    "email_subject": "¡Has recibido un pago de Solid Steel!"
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": str(cantidad_retirar),
                            "currency": "USD"
                        },
                        "receiver": supplier_email,
                        "note": "Payment for services rendered",
                        "sender_item_id": sender_item_id
                    }
                ]
            })

            # Intenta crear el payout
            if payout.create(sync_mode=False):
                messages.success(request, "Dinero retirado con éxito.")
                return redirect("retirar_saldo")
            else:
                messages.error(request, "Error al procesar el retiro. Por favor, inténtalo de nuevo.")
                return redirect("retirar_saldo")
        else:
            messages.error(request, "Formulario inválido. Verifica la cantidad ingresada.")
            return redirect("retirar_saldo")

    messages.error(request, "Método no permitido.")
    return redirect("retirar_saldo")

def historial_compras_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión para ver tu historial de compras.")
        return redirect("client_login")

    client = Client.objects.get(user__id_user=user_id)
    historial = HistorialCompras.objects.filter(client=client)

    return render(request, "historial_compras.html", {"historial": historial})