"""
Django settings for SolidSteel project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(bco9)^g@zu52)zwrq8ms=zt@y6n62$1x4muag=f*chr4n+^06'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#NOOOOOOO BORRAAAR POORFAVOOOOOOR
ALLOWED_HOSTS = ['*'] 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login',
    'menu',
    'register',
    'about_us',
    'cart',
    'contact',
    'pay',
    'product',
    'recycler',
    'shipping',
    'supplier',
    'static',
    'client' ,
    
    #Google
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    
    #facerecognition

]

#se refiere a tomar informacion básica del profile and email para poder iniciar sesion
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

#id en el sitio de administrador de django
SITE_ID = 2  

#Para evitar el menú o pantalla intermedia de Google con inicio de sesion o registro
SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Para autenticación convencional
    'allauth.account.auth_backends.AuthenticationBackend',  # Para Google
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', #también estop
]

ROOT_URLCONF = 'SolidSteel.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Ruta para plantillas generales
        ],
        'APP_DIRS': True,  # Permite buscar plantillas en las carpetas de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SolidSteel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
#NOOOOOOO BORRAAAR POORFAVOOOOOOR
#DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.mysql',
        #'NAME': 'solid_db',  # El nombre que aparece en tu lista
        #'USER': 'root',     # Debe ser el nombre de tu usuario de PythonAnywhere
        #'PASSWORD': 'Cacahuate11%',
        #'HOST': 'ls-7c806381e95ae6fdea3561848f7aa12dbe862db9.cdqi0uqm4gv3.us-west-2.rds.amazonaws.com',  # Tu host de MySQL en PythonAnywhere
        #'PORT': '3306',  # Puerto estándar para MySQL
        #'OPTIONS': {
           #'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        #},
    #}
#}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Static files directories (carpeta de desarrollo para archivos estáticos)
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Carpeta general para archivos estáticos en desarrollo
]

# Carpeta donde se recopilarán todos los archivos estáticos para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directorio donde collectstatic guardará los archivos estáticos

# Configuración para archivos de medios (si usas archivos subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Directorio donde se guardarán los archivos de medios subidos por los usuarios


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'solidsteel117@gmail.com'  # Pon tu correo de Gmail aquí
EMAIL_HOST_PASSWORD = 'xkmvvebswhxvwiwi'  # La contraseña de aplicación de Google
DEFAULT_FROM_EMAIL = 'noreply@solidsteel.com'

#Redirect para google
LOGIN_REDIRECT_URL = '/products/'  # Redirige a la página de cliente
LOGOUT_REDIRECT_URL = '/login/'  # Redirige a la página de login

#acceso para rekognition en aws
AWS_ACCESS_KEY_ID = 'AKIA47CR2OAEE7ANHYMU'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'us-west-2'  # Cambia esto según tu región

#api paypal
#PAYPAL_CLIENT_ID = 'AUm2f3CYUOUlCmPOkAtA6kFWzjpY_yqDT9pBKLFpYZBR7ZW7Gl62dWqzb7CBqyb6cxJX_WQePKVj7A7E'
#PAYPAL_CLIENT_SECRET = 'EKgTR0HeavgN8LEYCRI_vOQDAW5WwKCHyVuVUBjThRFW_-z9sDmx-QQ5OOL9jwxoWBjo1OYrSzOcsi4Q'
#PAYPAL_MODE = 'sandbox'  # Asegúrate de que esté en 'sandbox' para pruebas



#Stripe
STRIPE_PUBLIC_KEY = ""
STRIPE_SECRET_KEY_TEST = "sk_test_51QGZYaKIVqnl5aZZLPrAwNWgMwRxAL7Ies2QuDqfN2ZigszcL7jfaG6eFQYGe57mCjH2yQ3MUa8XWq8TyXfEfEXf00T5ZEH2jQ"
STRIPE_WEBHOOK_SECRET = ""
REDIRECT_DOMAIN = 'https://3760-2806-2f0-3321-ef0b-b5c5-4855-fc7-9ea5.ngrok-free.app'

PAYPAL_CLIENT_ID = 'Ac5BQjW9bnHkgwXKnjQuNW9SkK16mz5UpHfvkKFKdib9UDpWTEQjKsyMaERUO_BcsPkSDmw9UANyuYIu'
PAYPAL_CLIENT_SECRET = 'EN91Qny9RUxxqPZYaETkQVSIJbxjEvEVpgnTYoVpbEUAwlqUTNL2u_10JGNnld0Zx9i6xiBRdtJF7v9d'
PAYPAL_MODE = 'sandbox'

#ship24
SHIP24_API_KEY = 'apik_whxXKXjidHeQeWqhKvVMbYfxe3L8QN'
SHIP24_WEBHOOK_SECRET = 'whs_RSnMsLUGtQbw4AK5jeNbV4Wm3Itd25'
SHIP24_WEBHOOK_URL = 'https://3760-2806-2f0-3321-ef0b-b5c5-4855-fc7-9ea5.ngrok-free.app/shipping/webhook/ship24/' 
#para aws:
#SHIP24_WEBHOOK_URL = 'https://solid-steels.com/shipping/webhook/ship24/' 


#ngrok pruebas
CSRF_TRUSTED_ORIGINS = [
    'https://3760-2806-2f0-3321-ef0b-b5c5-4855-fc7-9ea5.ngrok-free.app',  # poner su local
    #para aws:
    #'https://solid-steels.com/', 
]
CSRF_COOKIE_SECURE = False