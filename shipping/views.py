from django.shortcuts import render, get_object_or_404, redirect
from product.models import Order, Shipment, Payment, ShoppingCart, Client, ClientAddress
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.contrib import messages
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware
import re
import time

logger = logging.getLogger(__name__)

@csrf_exempt
def ship24_webhook(request):
    """
    Procesa el webhook de Ship24 y actualiza los datos de los envíos y eventos de seguimiento.
    """
    if request.method == "HEAD":
        logger.info("Webhook validado exitosamente con HEAD request.")
        return HttpResponse(status=200)

    if request.method == "POST":
        # Validar autorización
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {settings.SHIP24_WEBHOOK_SECRET}":
            logger.error("Autorización fallida.")
            return JsonResponse({"error": "No autorizado"}, status=401)

        try:
            payload = json.loads(request.body)
            trackings = payload.get("trackings", [])

            for tracking in trackings:
                tracking_number = tracking.get("tracker", {}).get("trackingNumber")
                events = tracking.get("events", [])

                # Buscar el envío asociado
                shipment = Shipment.objects.filter(shipment_tracking_number=tracking_number).first()
                if not shipment:
                    logger.warning(f"Envío no encontrado para: {tracking_number}")
                    continue

                for event in events:
                    status = event.get("status", "").lower()
                    status_milestone = event.get("statusMilestone", "")
                    occurrence_datetime = event.get("occurrenceDatetime", "")

                    try:
                        event_date = make_aware(datetime.fromisoformat(occurrence_datetime))
                    except ValueError:
                        logger.error(f"Fecha inválida: {occurrence_datetime}")
                        continue

                    # Registrar evento
                    if not shipment.events.filter(status=status, occurrence_datetime=event_date).exists():
                        shipment.events.create(
                            status=status,
                            occurrence_datetime=event_date,
                        )
                        logger.info(f"Evento registrado: {status} ({event_date})")

                    # Actualizar estado del envío
                    if status == "shipped":
                        if not shipment.shipment_date or shipment.shipment_date < event_date:
                            shipment.shipment_date = event_date
                            shipment.shipment_status = "Enviado"
                            shipment.save()
                            logger.info(f"Fecha de envío actualizada: {shipment.shipment_date}")

                    elif status == "delivered":
                        if not shipment.shipment_actual_delivery_date or shipment.shipment_actual_delivery_date < event_date:
                            shipment.shipment_actual_delivery_date = event_date
                            shipment.shipment_status = "Entregado"
                            shipment.save()
                            logger.info(f"Fecha de entrega actualizada: {shipment.shipment_actual_delivery_date}")

            return JsonResponse({"message": "Webhook procesado correctamente."}, status=200)

        except json.JSONDecodeError:
            logger.error("Error al parsear el JSON.")
            return JsonResponse({"error": "Payload inválido"}, status=400)
        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            return JsonResponse({"error": "Error inesperado"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)

def controlar_limite_solicitudes():
    """
    Pausa para cumplir con el límite de solicitudes por segundo de Ship24.
    """
    time.sleep(0.1)  # Pausa de 100ms entre solicitudes

def determinar_courier_code(tracking_number):
    """
    Determina el courierCode basado en el número de seguimiento o mediante reglas definidas.
    """
    couriers = [
        {"code": "dhl", "regex": r"^\d{10}$"},
        {"code": "fedex", "regex": r"^\d{12}$"},
        {"code": "ups", "regex": r"^\d{18}$"},
    ]
    for courier in couriers:
        if re.match(courier["regex"], tracking_number):
            return courier["code"]
    return None  # Retorna None si no se puede determinar el mensajero

def courier_requiere_datos_adicionales(courier_code):
    """
    Verifica si el mensajero requiere datos adicionales como código postal y código de país.
    """
    couriers_requiring_data = ["fedex", "ups"]
    return courier_code in couriers_requiring_data


def actualizar_rastreador_ship24(tracker_id, courier_code):
    """
    Actualiza un tracker existente en Ship24.
    """
    try:
        validate_courier_code(courier_code)
    except ValueError as e:
        logger.error(f"Código de mensajero inválido: {e}")
        return False

    url = f"https://api.ship24.com/public/v1/trackers/{tracker_id}"
    headers = {
        "Authorization": f"Bearer {settings.SHIP24_API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        "courierCode": [courier_code],
    }

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Tracker actualizado correctamente: {tracker_id}")
        return True
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Error HTTP al actualizar tracker: {http_err}")
    except Exception as e:
        logger.error(f"Error inesperado al actualizar tracker: {e}")
    return False

# Vista principal de la app shipping
def shipping(request):
    return render(request, 'shipping/shipping.html')


def shipping_actualizar_datos(request):
    return render(request, 'shipping/shipping_actualizar_datos.html')

# Vista para mostrar los pedidos pagados
def paid_orders(request):
    # Obtiene el ID de usuario de la sesión y verifica que esté autenticado
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect('client_login')

    # Busca al cliente basado en el ID de usuario
    client = get_object_or_404(Client, user_id=user_id)

    # Filtra envíos pendientes del usuario
    shipments = Shipment.objects.filter(
        order__client=client,
        shipment_status="Pendiente"
    )

    # Determina si existen envíos pendientes
    has_pending_shipments = shipments.exists()

    # Envía los datos de envíos y el indicador de envíos pendientes al template
    return render(request, 'shipping/shipment_tracking_info.html', {
        'shipments': shipments,
        'client': client,
        'has_pending_shipments': has_pending_shipments
    })


# Vista para mostrar detalles de un envío específico y obtener información de Ship24
def shipment_tracking_info(request, tracking_number):
    """
    Muestra la información de un envío específico usando eventos almacenados localmente.
    """
    shipment = Shipment.objects.filter(shipment_tracking_number=tracking_number).first()

    if not shipment:
        messages.error(request, "Envío no encontrado")
        return redirect("paid_orders")

    # Obtener los eventos relacionados con el envío
    tracking_events = shipment.events.order_by('-occurrence_datetime')

    return render(request, 'shipping/shipment_info.html', {
        'shipment': shipment,
        'tracking_events': tracking_events,
    })
    
@login_required
def tracking_overview(request):
    user_id = request.user.id  # Suponiendo que el usuario está autenticado
    shipments = Shipment.objects.filter(order_clientuser_id_user=user_id)
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
    """
    Valida si el código de mensajero es válido.
    """
    obsolete_codes = ['ObsoleteCourierCode1', 'ObsoleteCourierCode2']
    if courier_code in obsolete_codes:
        logger.error(f"Código de mensajero inválido: {courier_code}")
        raise ValueError(f"El mensajero {courier_code} está obsoleto y no debe usarse.")
    logger.info(f"Código de mensajero válido: {courier_code}")
