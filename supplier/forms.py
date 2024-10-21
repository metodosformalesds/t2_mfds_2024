from django import forms
from product.models import Supplier

class SupplierForm(forms.ModelForm):
    user_email = forms.EmailField()  # Campo de email del usuario
    user_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False  # No requerido, solo si desean cambiar la contraseña
    )

    class Meta:
        model = Supplier
        fields = ['supplier_name', 'supplier_address', 'supplier_state', 'supplier_city', 'supplier_zip_code']
