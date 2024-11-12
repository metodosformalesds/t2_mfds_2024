from django.shortcuts import render, get_object_or_404, redirect
from product.models import Order, Shipment, Payment, ShoppingCart
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)

@csrf_exempt
def ship24_webhook(request):
    ship24_webhook_secret = settings.SHIP24_WEBHOOK_SECRET  

    if request.method == 'HEAD':
        return HttpResponse(status=200)

    elif request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != f'Bearer {ship24_webhook_secret}':
            logger.warning("Solicitud no autorizada: El secreto de autorización no coincide")
            return JsonResponse({"error": "No autorizado"}, status=401)

        logger.info("Webhook autorizado recibido en ship24_webhook")
        try:
            data = json.loads(request.body)
            trackings = data.get('trackings', [])
            if not trackings:
                return JsonResponse({"error": "No se encontraron datos de seguimiento"}, status=400)

            # Cargar el archivo de mensajeros para verificar códigos obsoletos
            couriers_data = pd.read_csv('/mnt/data/ship24-couriers.csv')

            for tracking in trackings:
                tracking_number = tracking.get('tracker', {}).get('trackingNumber')
                courier_code = tracking.get('tracker', {}).get('courierCode')
                events = tracking.get('events', [])

                # Verificar si el courier_code es obsoleto
                if courier_code:
                    courier_info = couriers_data[couriers_data['code'] == courier_code]
                    if not courier_info.empty and courier_info['is_deprecated'].values[0] == 1:
                        # Si es obsoleto, reemplazarlo con uno válido
                        alternate_courier = couriers_data[(couriers_data['is_deprecated'] == 0) & (couriers_data['country_code'].notna())].iloc[0]
                        courier_code = alternate_courier['code']
                        logger.info(f"Reemplazando courier obsoleto por {courier_code}")

                for event in events:
                    status = event.get('status')
                    occurrence_datetime = event.get('occurrenceDatetime')
                    status_code = event.get('statusCode')
                    status_category = event.get('statusCategory')
                    status_milestone = event.get('statusMilestone')

                    if tracking_number and status and occurrence_datetime:
                        shipment = Shipment.objects.filter(shipment_tracking_number=tracking_number).first()
                        if shipment:
                            # Asignar el courierCode si está disponible
                            if courier_code:
                                shipment.set_courier_codes([courier_code])
                            
                            # Verificar si el evento es más reciente que el último registrado
                            if not shipment.last_event_date or occurrence_datetime > shipment.last_event_date:
                                # Actualizar los campos de estado en el modelo Shipment
                                shipment.shipment_status = status
                                shipment.last_event_date = occurrence_datetime
                                shipment.status_code = status_code
                                shipment.status_category = status_category
                                shipment.status_milestone = status_milestone
                                shipment.save()
                                logger.info(f"Estado actualizado a {status} para el envío {tracking_number}")
                        else:
                            logger.warning(f"Envío no encontrado para el número de seguimiento: {tracking_number}")

            return JsonResponse({"message": "Actualizaciones de estado procesadas correctamente"}, status=200)
        except json.JSONDecodeError:
            logger.error("Error: JSON no válido")
            return JsonResponse({"error": "JSON no válido"}, status=400)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({"error": f"Error al procesar el webhook: {str(e)}"}, status=400)
    else:
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
    
@login_required
def tracking_overview(request):
    user_id = request.user.id  # Suponiendo que el usuario está autenticado
    shipments = Shipment.objects.filter(order__client__user__id_user=user_id)
    return render(request, 'shipping/tracking_overview.html', {'shipments': shipments})

def track_shipment_with_additional_info(shipment, destination_postcode, destination_country_code):
    # Verifica si el mensajero requiere estos datos
    if shipment.shipment_carrier == 'CourierCodeRequiereDatosAdicionales':
        if not destination_postcode or not destination_country_code:
            raise ValueError("Se requiere el código postal y el código de país del destinatario.")
    
    # Lógica para hacer el seguimiento con la API de Ship24, con los datos adicionales
    api_url = f"https://api.ship24.com/trackings/{shipment.shipment_tracking_number}"
    data = {
        'destinationPostCode': destination_postcode,
        'destinationCountryCode': destination_country_code,
        # Otros parámetros...
    }
    response = requests.post(api_url, json=data)
    return response.json()

def get_couriers(request):
    url = 'https://api.ship24.com/couriers'
    headers = {
        'Authorization': f'Bearer {settings.SHIP24_API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        couriers = response.json()
        return JsonResponse(couriers, safe=False)
    else:
        return JsonResponse({'error': 'Error al obtener los mensajeros'}, status=400)


def validate_courier_code(courier_code):
    if courier_code in ['ObsoleteCourierCode1', 'ObsoleteCourierCode2']:
        raise ValueError(f"El mensajero {courier_code} está obsoleto y no debe usarse.")