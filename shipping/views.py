from django.shortcuts import render, get_object_or_404, redirect
from product.models import Order, Shipment, Payment, ShoppingCart
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def ship24_webhook(request):
    if request.method == 'POST':
        logger.info("Webhook recibido en ship24_webhook")
        try:
            data = json.loads(request.body)
            logger.info(f"Datos recibidos: {data}")
            tracking_number = data.get('tracking_number')
            status = data.get('status')
            if not tracking_number or not status:
                return JsonResponse({"error": "Faltan campos requeridos"}, status=400)
            
            # Lógica de actualización del estado del envío
            shipment = Shipment.objects.filter(shipment_tracking_number=tracking_number).first()
            if shipment:
                shipment.shipment_status = status
                shipment.save()
                return JsonResponse({"message": "Estado actualizado correctamente"}, status=200)
            else:
                return JsonResponse({"error": "Envío no encontrado"}, status=404)
        except json.JSONDecodeError:
            logger.error("Error: JSON no válido")
            return JsonResponse({"error": "JSON no válido"}, status=400)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({"error": f"Error al procesar el webhook: {str(e)}"}, status=400)
    logger.warning("Método no permitido")
    return JsonResponse({"error": "Método no permitido"}, status=405)

# Vista principal de la app shipping
def shipping(request):
    return render(request, 'shipping/shipping.html')

# Vista para actualizar datos (puedes personalizar esta según la lógica que necesites)
def shipping_actualizar_datos(request):
    return render(request, 'shipping/shipping_actualizar_datos.html')

# Vista para mostrar los pedidos pagados
def paid_orders(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect('client_login')

    # Obtener envíos pendientes del usuario
    shipments = Shipment.objects.filter(
        order__client__user__id_user=user_id,
        shipment_status="Pendiente"
    )

    # Depuración: imprime cada número de seguimiento
    for shipment in shipments:
        print(f"ID de Envío: {shipment.id_shipment}, Número de Seguimiento: '{shipment.shipment_tracking_number}'")

    return render(request, 'shipping/paid_orders.html', {'shipments': shipments})


# Vista para mostrar detalles de un envío específico y obtener información de Ship24

def shipment_tracking_info(request, tracking_number):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.")
        return redirect('client_login')
    
    # Verificar que el cliente tenga un envío con ese número de seguimiento
    shipment = Shipment.objects.filter(
        shipment_tracking_number=tracking_number,
        order__client__user__id_user=user_id
    ).first()

    if not shipment:
        messages.error(request, "Envío no encontrado para este usuario.")
        return redirect('paid_orders')

    # Verificar y mostrar el número de seguimiento para depuración
    print("Número de seguimiento encontrado:", shipment.shipment_tracking_number)

    # Obtener el seguimiento del API de Ship24
    api_key = settings.SHIP24_API_KEY
    url = f"https://api.ship24.com/trackings/{tracking_number}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levanta una excepción para códigos de error HTTP
        data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, "Hubo un error al obtener el estado de seguimiento. Inténtalo más tarde.")
        return redirect('paid_orders')
    except ValueError:
        messages.error(request, "La respuesta de seguimiento no es válida.")
        return redirect('paid_orders')

    # Renderizar la plantilla con la información de seguimiento
    return render(request, 'shipping/shipment_tracking_info.html', {'shipment': data, 'shipment_record': shipment})
