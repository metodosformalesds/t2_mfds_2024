from product.models import ShoppingCart, Client, UserAccount

def cart_items_count(request):

    """
    Context Processor Name: Contador de elementos en el carrito de compras
    File: context_processors.py
    Author: Berenice Flores Hernández

    Descripción:
        Este contexto procesador calcula y devuelve el número de elementos en el carrito de compras del usuario.
        Se utiliza para mostrar un contador en el botón del carrito en las plantillas de la aplicación.

    Características principales:
        - Verifica si existe un usuario autenticado basado en la sesión.
        - Obtiene el conteo de elementos en el carrito sumando las cantidades de productos en el carrito del usuario.
        - Devuelve el número total de elementos en el carrito como contexto para las plantillas.

    Notas:
        - Requiere que el modelo UserAccount, Client y ShoppingCart estén correctamente definidos en product.models.
        - Asegura que la sesión del usuario contenga el ID correcto para identificar al usuario.
    """
  
    if not request.session.get('user_id'):
        return {'cart_items_count': 0}

    try:
        user_account = UserAccount.objects.get(id_user=request.session['user_id'])
        client = Client.objects.get(user=user_account)
        cart_items = ShoppingCart.objects.filter(client=client)
        count = sum(item.cart_product_quantity for item in cart_items)
        return {'cart_items_count': count}
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        return {'cart_items_count': 0}
