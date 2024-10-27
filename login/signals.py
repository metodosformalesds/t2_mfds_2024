from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from product.models import UserAccount, UserRole
from django.contrib import messages

#El archivo sirve para que los clientes se puedan reconocer como clientes de Google
@receiver(user_signed_up)
def create_user_account_on_signup(sender, request, user, **kwargs):
    """Crea un registro en UserAccount cuando un usuario se registra con Google."""
    account, created = UserAccount.objects.get_or_create(
        user_email=user.email,
        defaults={
            'user_role': UserRole.CLIENT,  # Asigna el rol CLIENT automáticamente
        }
    )
    if created:
        messages.success(request, 'Se ha creado tu cuenta correctamente.')

@receiver(user_logged_in)
def ensure_user_account_exists_on_login(sender, request, user, **kwargs):
    """Asegura que el usuario tenga un registro en UserAccount al iniciar sesión y sincroniza la sesión."""
    account, created = UserAccount.objects.get_or_create(
        user_email=user.email,
        defaults={
            'user_role': UserRole.CLIENT,  # Asigna el rol CLIENT automáticamente si no existe
        }
    )

    # Sincronizar la sesión con los datos del usuario
    request.session['user_id'] = account.id_user
    request.session['user_email'] = account.user_email
    request.session['user_role'] = account.user_role
