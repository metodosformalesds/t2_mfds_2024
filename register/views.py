"""
Module: Registro de Usuarios con Validación Biométrica
Author: César Andrade
Coauthor: Hugo Abisai Reyes Trejo - 215201
Description:
    Este módulo implementa funcionalidades avanzadas para el registro de usuarios (proveedores y clientes) con validación
    biométrica. Se utiliza Amazon Rekognition para verificar coincidencias faciales entre una identificación oficial y
    una foto actual capturada o subida por el usuario. También incluye detección de palabras clave en documentos para
    garantizar la validez de las identificaciones.

Features:
    - Registro de proveedores y clientes:
        - Validación de identificaciones oficiales mediante detección de palabras clave en imágenes.
        - Comparación de rostros entre una identificación oficial y una foto actual.
        - Manejo de imágenes capturadas por cámara o cargadas a través de un código QR único.
        - Validación de que las imágenes no sean idénticas para evitar fraudes.
    - Carga de imágenes en una carpeta temporal (`temp`) para procesamiento.
    - Eliminación automática de archivos temporales después del uso.
    - Mensajes de error y éxito para guiar al usuario durante el proceso.

Functions:
    - `create_rekognition_client()`: Crea y configura un cliente de Amazon Rekognition.
    - `detect_keywords_in_document(image_path, keywords)`: Detecta palabras clave en un documento utilizando OCR de Rekognition.
    - `detect_face(image_path)`: Detecta rostros en una imagen.
    - `compare_faces_with_rekognition(identificacion_path, foto_actual_path)`: Compara dos imágenes para determinar si los rostros coinciden.
    - `are_images_identical(identificacion_path, foto_actual_path)`: Verifica si dos imágenes son idénticas en contenido.
    - `supplier_register(request)`: Gestiona el registro de proveedores con validación biométrica.
    - `client_register(request)`: Gestiona el registro de clientes con validación biométrica.
    - `cargar_foto(request, unique_id)`: Permite cargar una foto mediante un identificador único generado dinámicamente.

Notes:
    - Se utilizan las credenciales configuradas en `settings.py` para acceder a Amazon Rekognition.
    - La carpeta `temp` se utiliza como almacenamiento temporal para las imágenes procesadas.
    - Las palabras clave incluyen términos comunes en documentos oficiales como licencias, pasaportes y credenciales de elector.
    - El umbral de similitud facial se configura en 90% para considerar coincidencias válidas.

Error Handling:
    - Si las imágenes no son válidas o no cumplen con las condiciones, se muestran mensajes específicos al usuario.
    - Manejo de errores en la carga de imágenes y validaciones biométricas para asegurar una experiencia fluida.

Dependencies:
    - Amazon Rekognition (boto3)
    - Django: settings, mensajes, almacenamiento y renderizado de plantillas.
"""

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


# Crear cliente de Amazon Rekognition
def create_rekognition_client():
    return boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
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

# Función para detectar si una imagen contiene un rostro
def detect_face(image_path):
    rekognition = create_rekognition_client()
    with open(image_path, 'rb') as image_file:
        response = rekognition.detect_faces(
            Image={'Bytes': image_file.read()},
            Attributes=['ALL']
        )
    return len(response['FaceDetails']) > 0




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

# Función para verificar que las imágenes no sean las mismas
def are_images_identical(identificacion_path, foto_actual_path):
    # Compara el contenido binario de los dos archivos
    with open(identificacion_path, 'rb') as img1, open(foto_actual_path, 'rb') as img2:
        return img1.read() == img2.read()


# Definimos para manejar el registro de proveedor
def supplier_register(request):
    if request.method == 'POST':
        
        form = SupplierRegisterForm(request.POST, request.FILES)
        unique_id = request.POST.get('unique_id')
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el correo ya está registrado
            if UserAccount.objects.filter(user_email=email).exists():
                messages.error(request, 'El correo ya está registrado. Por favor, usa otro.')
            else:
                # Verifica que la carpeta 'temp' exista
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                # Obtener los archivos de las imágenes
                identificacion_img = request.FILES['identificacion']
                # Define rutas de guardado
                identificacion_path = os.path.join(temp_dir, 'identificacion.jpg')


                # Guarda las imágenes manualmente en la carpeta 'temp'
                with open(identificacion_path, 'wb') as f:
                    f.write(identificacion_img.read())

                # Verificar si la foto actual se tomó con la cámara o si se subió a través del QR
                # Lógica para `foto_actual`
                if 'foto_actual' in request.FILES:  # Si la foto fue tomada con la cámara
                    foto_actual_img = request.FILES['foto_actual']
                    foto_actual_path = os.path.join(temp_dir, 'foto_actual.jpg')
                    with open(foto_actual_path, 'wb') as f:
                        f.write(foto_actual_img.read())
                else:  # Si la foto fue subida mediante el QR
                    foto_actual_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}.jpg")
                    if not os.path.exists(foto_actual_path):
                        messages.error(request, 'No se encontró la foto subida. Asegúrate de subir tu foto correctamente, o utilizando el qr.')
                        return render(request, 'home/supplier_register.html', {'form': form})       

                try:
                    # Definir mensajes
                    success_message = 'Proveedor registrado exitosamente'
                    face_mismatch_message = 'Los rostros no coinciden.'
                    invalid_document_message = 'Identificación no válida. Asegúrate de tomar bien la foto y que sea una identificación oficial.'
                
                    # Verificar condiciones
                    if not detect_keywords_in_document(identificacion_path, KEYWORDS):
                        messages.error(request, invalid_document_message)
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif not detect_face(identificacion_path):
                        messages.error(request, 'La identificación no muestra bien el rostro.')
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif not detect_face(foto_actual_path):
                        messages.error(request, 'La foto actual no muestra bien el rostro.')
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif are_images_identical(identificacion_path, foto_actual_path):
                        messages.error(request, 'La foto actual no debe ser la misma que la identificación. Por favor, sube una foto diferente.')
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif not compare_faces_with_rekognition(identificacion_path, foto_actual_path):
                        messages.error(request, face_mismatch_message)
                        return render(request, 'home/supplier_register.html', {'form': form})
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
            print("Errores del formulario:", form.errors)
            messages.error(request, 'El formulario no es válido. Revisa los datos.')
        
    else:
        form = SupplierRegisterForm()

    return render(request, 'home/supplier_register.html', {'form': form})


def client_register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST, request.FILES)
        unique_id = request.POST.get('unique_id')
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el correo ya está registrado
            if UserAccount.objects.filter(user_email=email).exists():
                messages.error(request, 'El correo ya está registrado. Por favor, usa otro.')
            else:
                # Crear directorio temporal si no existe
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Obtener imágenes de identificación y foto actual
                identificacion_img = request.FILES['identificacion']
                # Definir rutas temporales para guardar las imágenes
                identificacion_path = os.path.join(temp_dir, 'identificacion.jpg')

                # Guardar las imágenes en las rutas temporales
                with open(identificacion_path, 'wb') as f:
                    f.write(identificacion_img.read())

                                # Verificar si la foto actual se tomó con la cámara o si se subió a través del QR
                # Lógica para `foto_actual`
                if 'foto_actual' in request.FILES:  # Si la foto fue tomada con la cámara
                    foto_actual_img = request.FILES['foto_actual']
                    foto_actual_path = os.path.join(temp_dir, 'foto_actual.jpg')
                    with open(foto_actual_path, 'wb') as f:
                        f.write(foto_actual_img.read())
                else:  # Si la foto fue subida mediante el QR
                    foto_actual_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}.jpg")
                    if not os.path.exists(foto_actual_path):
                        messages.error(request, 'No se encontró la foto subida. Asegúrate de subir tu foto correctamente, o utilizando el qr.')
                        return render(request, 'home/client_register.html', {'form': form})    

                try:
                    # Verificar condiciones
                    if not detect_keywords_in_document(identificacion_path, KEYWORDS):
                        messages.error(request, 'Identificación no válida. Asegúrate de que sea una identificación oficial.')
                    elif not detect_face(identificacion_path):
                        messages.error(request, 'La identificación no muestra claramente el rostro.')
                    elif not detect_face(foto_actual_path):
                        messages.error(request, 'La foto actual no muestra claramente el rostro.')
                    elif are_images_identical(identificacion_path, foto_actual_path):
                        messages.error(request, 'Las imágenes no deben ser idénticas. Sube fotos diferentes.')
                    elif not compare_faces_with_rekognition(identificacion_path, foto_actual_path):
                        messages.error(request, 'Los rostros no coinciden.')
                    else:
                        # Guarda el cliente y muestra mensaje de éxito
                        form.save()
                        messages.success(request, 'Cliente registrado exitosamente')
                        return redirect('client_login')  # Redirige al login de usuarios normales
                finally:
                    # Eliminar archivos temporales después de usarlos
                    if os.path.exists(identificacion_path):
                        os.remove(identificacion_path)
                    if os.path.exists(foto_actual_path):
                        os.remove(foto_actual_path)
        else:
            messages.error(request, 'El formulario no es válido. Revisa los datos.')
    else:
        form = ClientRegisterForm()

    return render(request, 'home/client_register.html', {'form': form})


import os
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse

def cargar_foto(request, unique_id):
    if request.method == 'POST' and request.FILES.get('foto'):
        foto = request.FILES['foto']
        # Guardar la foto con el nombre de la ID única
        foto_name = f"{unique_id}.jpg"  # Asegúrate de que el nombre esté correcto
        foto_path = os.path.join(settings.MEDIA_ROOT, foto_name)
        
        try:
            default_storage.save(foto_path, foto)
            messages.success(request, 'Foto cargada correctamente, termina de rellenar el formulario!')
        except Exception as e:
            # Manejar cualquier error durante la carga
            messages.error(request, 'La foto no pudo ser cargada correctamente, vuelve a intentarlo.')
            print(f"Error al guardar la foto: {e}")

        return render(request, 'home/cargar_foto.html', {'unique_id': unique_id})
    
    return render(request, 'home/cargar_foto.html', {'unique_id': unique_id})

