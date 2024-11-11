import requests

api_key = 'apik_whxXKXjidHeQeWqhKvVMbYfxe3L8QN'
tracking_number = 'TRACK1120241111183833'  # Usa un número de seguimiento válido
url = f'https://api.ship24.com/trackings/{tracking_number}'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)
print("Response Text:", response.text)  # Muestra el texto completo de la respuesta

# Intenta decodificar como JSON sólo si hay contenido
if response.status_code == 200 and response.text:
    try:
        print("Response JSON:", response.json())
    except requests.exceptions.JSONDecodeError as e:
        print("Error al decodificar JSON:", e)
else:
    print("Error: La API devolvió un código de estado", response.status_code)
