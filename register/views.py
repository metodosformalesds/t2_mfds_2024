
#Dependencias para reconociminiento de imagne
import boto3
from django.conf import settings
from django.core.files.storage import default_storage
import os

#dependencias previas
from django.shortcuts import render, redirect
from django.contrib import messages

#dependencias de la base de datos
from product.models import Supplier, UserAccount  # Importamos los modelos

#dependencias del los formularios
from .forms import SupplierRegisterForm
from .forms import ClientRegisterForm

#codigo para crear un archivo temporal para las imagenes del reconocimiento
if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp')):
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp'))
    
# Definir las palabras clave que estamos buscando
KEYWORDS = [
    # Comunes en todos los documentos
    "nombre", "apellidos", "sexo", "fecha de nacimiento", "curp", "firma", "domicilio",
    
    # Credencial de Elector (INE - México)
    "clave de elector", "instituto nacional electoral", "credencial para votar", "vigencia",
    "estado", "municipio", "sección", "emisión", "clave única de registro de población",
    
    # Licencia de Conducir (México y Estados Unidos)
    "licencia para conducir", "chofer particular", "estado de chihuahua", "permiso", "número de licencia",
    "driver license", "license number", "restriction", "class", "expires", "birth date",
    
    # Pasaporte (México y Estados Unidos)
    "pasaporte", "passport", "passport number", "country of issuance", "nationality",
    "date of birth", "place of birth", "surname", "given name", "date of issue", "expiry date",
    "passport card", "united states of america", "estados unidos mexicanos",
    
    # Tarjeta de Residencia (Green Card - Estados Unidos)
    "permanent resident", "uscis", "alien number", "resident since", "category",
    "given names", "country of birth", "uscis number",
    
    # Identification Card (Estados Unidos)
    "identification card", "texas", "state id", "id number", "dob", "expiration date",
    "sample", "address", "city", "zip code", "date issued",
    
    # Información adicional para asegurar la detección
    "issued", "expires", "height", "weight", "eyes", "hair", "organ donor", "veteran",
    "category", "identificación oficial", "número de identificación", "estado", "municipio",
    "expedición", "nacionalidad", "identificación", "clase", "restricciones"
]

# Función para detectar palabras clave en el texto extraído
def detect_keywords_in_document(image_path, keywords):
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    with open(image_path, 'rb') as image_file:
        response = rekognition.detect_text(Image={'Bytes': image_file.read()})

    # Lista para almacenar todas las palabras detectadas
    detected_words = set()

    # Extraer todas las palabras y líneas detectadas en la imagen
    for text in response['TextDetections']:
        # Convertir el texto detectado a minúsculas para la comparación
        detected_text = text['DetectedText'].lower()
        
        # Agregar cada palabra a detected_words
        if text['Type'] == 'WORD':
            detected_words.add(detected_text)
        elif text['Type'] == 'LINE':
            # Para cada línea completa, revisa si contiene alguna palabra clave
            for keyword in keywords:
                if keyword.lower() in detected_text:  # Coincidencia parcial en línea completa
                    detected_words.add(keyword.lower())  # Agregar solo la palabra clave, no el texto completo

    # Contar el número de palabras clave que aparecen en el texto detectado
    found_keywords = sum(1 for keyword in keywords if keyword.lower() in detected_words)

    # Retorna True si al menos 2 palabras clave son encontradas
    return found_keywords >= 2


#funcion que compara las imagenes de la identificacion con la cara en tiempo real
def compare_faces_with_rekognition(identificacion_path, foto_actual_path):
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    with open(identificacion_path, 'rb') as source_image, open(foto_actual_path, 'rb') as target_image:
        response = rekognition.compare_faces(
            SourceImage={'Bytes': source_image.read()},
            TargetImage={'Bytes': target_image.read()}
        )

    for face_match in response['FaceMatches']:
        similarity = face_match['Similarity']
        if similarity > 90:  # Puedes ajustar el umbral de similitud
            return True

    return False



# Definimos la vista para manejar el registro de proveedor
def supplier_register(request):
    if request.method == 'POST':
        form = SupplierRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # Verifica que la carpeta 'temp' exista
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Obtener los archivos de las imágenes
            identificacion_img = request.FILES['identificacion']
            foto_actual_img = request.FILES['foto_actual']

            # Define rutas de guardado
            identificacion_path = os.path.join(temp_dir, 'identificacion.jpg')
            foto_actual_path = os.path.join(temp_dir, 'foto_actual.jpg')

            # Guarda las imágenes manualmente en la carpeta 'temp'
            with open(identificacion_path, 'wb') as f:
                f.write(identificacion_img.read())
            with open(foto_actual_path, 'wb') as f:
                f.write(foto_actual_img.read())

            try:
                # Compara las imágenes usando Rekognition
                match = compare_faces_with_rekognition(identificacion_path, foto_actual_path)
                
                # Detecta palabras clave en el documento usando Rekognition
                valid_document = detect_keywords_in_document(identificacion_path, KEYWORDS)

                # Definir mensajes
                success_message = 'Proveedor registrado exitosamente'
                face_mismatch_message = 'Los rostros no coinciden.'
                invalid_document_message = 'Identificación no válida. Asegúrate de tomar bien la foto y que sea una identificación oficial.'
                
                # Verificar condiciones
                if not valid_document:
                    messages.error(request, invalid_document_message)
                elif not match:
                    messages.error(request, face_mismatch_message)
                else:
                    form.save()
                    messages.success(request, success_message)
                    return redirect('supplier_login')  # Redirigir a la página de inicio de sesión
                
            finally:
                # Eliminar archivos temporales después de usarlos
                if os.path.exists(identificacion_path):
                    os.remove(identificacion_path)
                if os.path.exists(foto_actual_path):
                    os.remove(foto_actual_path)
        else:
            messages.error(request, 'El formulario no es válido. Revisa los datos.')
        
    else:
        form = SupplierRegisterForm()

    return render(request, 'home/supplier_register.html', {'form': form})


# Vista para el registro de clientes
def client_register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el correo ya está registrado
            if UserAccount.objects.filter(user_email=email).exists():
                messages.error(request, 'El correo ya está registrado. Por favor, usa otro.')
            else:
                form.save()  # Guardamos el cliente y el usuario
                messages.success(request, 'Cliente registrado exitosamente')
                return redirect('client_login')  # Redirige al login de usuarios normales
    else:
        form = ClientRegisterForm()

    return render(request, 'home/client_register.html', {'form': form})