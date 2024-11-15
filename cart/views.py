from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from product.models import Product, ShoppingCart, UserAccount, Client, Payment, Order, ClientAddress, OrderItem

from django.conf import settings
from django.http import HttpResponse
from django.db import transaction
import stripe
import time
from django.http import JsonResponse 
import pandas as pd


# Vista para mostrar el carrito
def cart(request):
    # Obtener el ID del usuario desde la sesión
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        # Mostrar un mensaje de error si no hay una sesión activa
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        # Redirigir al usuario a la página de inicio de sesión
        return redirect('client_login')

    # Obtener el UserAccount y Client asociado al user_id en la sesión
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('login')
    
    # Obtener items del carrito solo para este cliente
    carrito_items = ShoppingCart.objects.filter(client=client)
    total = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)

    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    if request.method == 'POST':
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items=[{
                    'price_data': {
                        'currency': 'mxn',
                        'product_data': {
                            'name': 'Carrito de compras',
                        },
                        'unit_amount': int(total * 100),  # Stripe requiere centavos (2000 = $20.00)
                    },
                    'quantity': 1,
                }],

            mode = 'payment',
            customer_creation = 'always',
            success_url = settings.REDIRECT_DOMAIN + '/cart/payment_successful?session_id={CHECKOUT_SESSION_ID}',
			cancel_url = settings.REDIRECT_DOMAIN + '/cart/payment_cancelled',

        )

        return redirect(checkout_session.url, code = 303)
    
    return render(request, 'cart/cart.html', {'carrito_items': carrito_items, 'total': total})

def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
        )
    except ValueError as e:
        return HttpResponse(status = 400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status = 400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)#
        time.sleep(15)
        user_payment = Payment.objects.get(stripe_checkout_id=session_id)#
        
        user_payment.payment_bool = True
        user_payment.save()
    return HttpResponse(status = 200)

#4242424242424242
def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)

    # Extrae el correo electrónico del cliente desde la sesión de Stripe
    customer_email = session.get('customer_email', None)
    
    user_id = request.session.get('user_id')
    user_account = UserAccount.objects.get(id_user=user_id)
    client = Client.objects.get(user=user_account)

    # Obtener items del carrito y calcular el total
    carrito_items = ShoppingCart.objects.filter(client=client)
    subtotal = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)
    total = subtotal  # Si tienes impuestos u otros cálculos, ajústalo aquí

    # Extraer datos de la transacción
    transaction_id = session.payment_intent
    payment_date = timezone.now()  # Usar la fecha y hora actual
    payment_method = "Stripe"

    # Crear una nueva orden
    address = ClientAddress.objects.filter(client=client).first()
    order = Order.objects.create(
        client=client,
        address=address,
        order_date=payment_date
    )

    # Crear los items de la orden
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
        payment_status="Exitosa",  # Estado del pago
        app_user=client,
        stripe_checkout_id=checkout_session_id,
        payment_bool=True,
        customer_email=customer_email
    )

    # Limpia el carrito del usuario
    ShoppingCart.objects.filter(client=client).delete()

    # Pasar los datos al contexto para mostrarlos en la plantilla
    return render(request, 'cart/success.html', {
        'transaction_id': transaction_id,
        'payment_date': payment_date,
        'payment_method': payment_method,
        'subtotal': f"{subtotal:.2f}",  # Formatear a dos decimales
        'total': f"{total:.2f}",  # Formatear a dos decimales
        'status': "Exitosa",
        'customer_email': customer_email
    })


def payment_cancelled(request):
    return render(request, 'cart/cancel.html')


# Vista para agregar productos al carrito
def agregar_al_carrito(request, id):
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el UserAccount y Client asociado al user_id en la sesión
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('product_detail', id=id)

    producto = get_object_or_404(Product, id_product=id)
    cantidad = int(request.POST.get('cantidad', 1))

    # Obtener o crear el item en el carrito, asegurando que esté asociado al cliente específico
    cart_item, created = ShoppingCart.objects.get_or_create(
        client=client,
        product=producto,
        defaults={'cart_product_quantity': 0, 'cart_added_date': timezone.now()}
    )

    cantidad_total = cart_item.cart_product_quantity + cantidad
    if cantidad_total > producto.product_stock:
        messages.error(request, f"No hay suficiente stock de {producto.product_name}. Solo quedan {producto.product_stock - cart_item.cart_product_quantity} unidades.")
        return redirect('product_detail', id=id)

    # Actualizar cantidad sin modificar el stock del producto en la base de datos
    cart_item.cart_product_quantity = cantidad_total
    cart_item.save()
    return redirect('cart')

# Vista para restar una unidad de un producto del carrito
def restar_del_carrito(request, id):
    user_id = request.session.get('user_id')

    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el cliente actual y luego el item en el carrito
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('cart')

    carrito_item = get_object_or_404(ShoppingCart, client=client, product_id=id)
    cantidad = int(request.POST.get('cantidad', 1))

    if carrito_item.cart_product_quantity > cantidad:
        carrito_item.cart_product_quantity -= cantidad
        carrito_item.save()
    else:
        carrito_item.delete()
    return redirect('cart')


# Vista para eliminar productos del carrito
def eliminar_del_carrito(request, id):
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el cliente actual y luego el item en el carrito
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('cart')

    carrito_item = get_object_or_404(ShoppingCart, client=client, product_id=id)
    carrito_item.delete()
    return redirect('cart')


def drag_and_drop(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']

        try:
            # Leer el archivo Excel con pandas
            df = pd.read_excel(excel_file)
            # Convertir el DataFrame a una lista de listas (filas)
            data = df.fillna('').values.tolist()  # Rellenar valores NaN con cadenas vacías
            headers = df.columns.tolist()  # Obtener los encabezados de las columnas

            print("Encabezados:", headers)  # Imprimir los encabezados en la consola
            print("Datos:", data)  # Imprimir los datos en la consola

            # Enviar los datos del Excel como respuesta JSON
            return JsonResponse({"success": True, "headers": headers, "data": data})
        except Exception as e:
            print(f"Error al procesar el archivo: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, 'cart/drag.html')
