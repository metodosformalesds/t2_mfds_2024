
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

                if match:
                    form.save()
                    messages.success(request, 'Proveedor registrado exitosamente')
                    return redirect('supplier_login')  # Redirigir a la página de inicio de sesión
                else:
                    messages.error(request, 'Los rostros no coinciden!.')
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