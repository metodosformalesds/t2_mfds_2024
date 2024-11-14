from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment as PayPalPayment
from product.models import ShoppingCart, UserAccount, Client, Supplier, SupplierPaymentMethodModel,ClientAddress,OrderItem,Order,Payment
from django.views.decorators.http import require_POST
from .paypal import paypalrestsdk
from django.db import transaction
from django.http import JsonResponse
from supplier.forms import WithdrawForm
import random
import string
from django.utils import timezone

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

    # Ejecutar el pago en PayPal
    pago = PayPalPayment.find(payment_id)  # Cambiar a PayPalPayment
    user_account = UserAccount.objects.get(id_user=user_id)
    client = Client.objects.get(user=user_account)

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
        messages.error(request, "Error al confirmar el pago")
        return redirect("cart/error")



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

from django.contrib import messages

def create_payout(request):
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
            supplier_email = payment_method.supplier_payment_email  # Reemplaza con el email correcto
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": sender_batch_id,
                    "email_subject": "¡Has recibido un pago de Solid Steel!"
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
