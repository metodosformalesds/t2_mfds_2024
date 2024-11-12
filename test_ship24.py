import requests

url = "https://3ac9954efe579fcc1c7090dfdb3ed318.serveo.net/webhook/ship24/"
response = requests.head(url)

if response.status_code == 200:
    print("La URL del webhook está activa y responde con 200 OK")
else:
    print(f"Error: La URL del webhook respondió con {response.status_code}")
