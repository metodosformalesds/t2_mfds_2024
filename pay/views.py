from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment
from product.models import ShoppingCart, UserAccount, Client, Supplier, SupplierPaymentMethodModel, Order, Shipment
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
import logging
from django.http import JsonResponse, HttpResponse




logger = logging.getLogger(__name__)
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
    pago = Payment({
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
    
    # Ejecutar el pago en PayPal
    pago = Payment.find(payment_id)
    if pago.execute({"payer_id": payer_id}):
        messages.success(request, "Pago completado con éxito")
        
        user_id = request.session.get('user_id')
        client = Client.objects.get(user__id_user=user_id)
        carrito_items = ShoppingCart.objects.filter(client=client)

        # Crear pedido y agregar productos
        nuevo_pedido = Order.objects.create(
            client=client,
            address=client.clientaddress_set.first(),
            order_date=timezone.now()
        )
        for item in carrito_items:
            nuevo_pedido.orderitem_set.create(
                product=item.product,
                quantity=item.cart_product_quantity,
                price_at_purchase=item.product.product_price
            )

        # Crear el envío y registrar el seguimiento en Ship24
        tracking_number = f"TRACK{nuevo_pedido.id_order}{timezone.now().strftime('%Y%m%d%H%M%S')}"
        nuevo_envio = Shipment.objects.create(
            order=nuevo_pedido,
            shipment_tracking_number=tracking_number,
            shipment_carrier="dhl",  # Reemplaza con el código de courier adecuado
            shipment_status="Pendiente",
            shipment_date=timezone.now(),
            shipment_estimated_delivery_date=timezone.now() + timezone.timedelta(days=7),
            shipment_actual_delivery_date=None
        )

        # Llamada a la API de Ship24
        api_key = settings.SHIP24_API_KEY
        url = "https://api.ship24.com/trackings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "trackingNumber": tracking_number,
            "courier": "DHL",  # Especifica el código del courier si es necesario
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            nuevo_envio.shipment_status = data.get("status", "Pendiente")
            nuevo_envio.save()
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error al iniciar el seguimiento en Ship24")
            logger.error(f"Error en la API de Ship24: {str(e)}")
            return redirect("cart")

        carrito_items.delete()
        return redirect("cart")
    else:
        messages.error(request, "Error al confirmar el pago")
        return redirect("cart")

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
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def create_payout(request):
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():
            cantidad_retirar = form.cleaned_data['cantidad']

        user_id = request.session.get('supplier_id')
        user = get_object_or_404(UserAccount, pk=user_id)
        supplier = get_object_or_404(Supplier, user=user)

        cantidad_retirar = float(request.POST.get("cantidad"))

        # Verifica si el balance es suficiente
        if float(cantidad_retirar) > float(supplier.balance):
            return JsonResponse({"status": "error", "message": "Saldo insuficiente para retirar esta cantidad."})

        # Descuenta la cantidad del balance
        supplier.balance -= cantidad_retirar
        supplier.save()

        # Genera IDs aleatorios para sender_batch_id y sender_item_id
        sender_batch_id = generar_id_unico()
        sender_item_id = generar_id_unico()

        # Configura el payout
        payment_method = get_object_or_404(SupplierPaymentMethodModel, supplier=supplier)
        supplier_email = payment_method.supplier_payment_email  # Reemplaza con el email correcto
        payout = paypalrestsdk.Payout({
            "sender_batch_header": {
                "sender_batch_id": sender_batch_id,
                "email_subject": "You've received a payment from [Your App Name]!"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(cantidad_retirar),  # Convertir a string para PayPal API
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
            return JsonResponse({
                "status": "success",
                "message": "Dinero retirado con éxito.",
                "nuevo_balance": supplier.balance,
                "payout_id": payout.batch_header.payout_batch_id
            })
        else:
            return JsonResponse({"status": "error", "error": payout.error})

    return JsonResponse({"status": "error", "message": "Solicitud inválida."})