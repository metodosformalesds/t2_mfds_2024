from django import forms
from product.models import Supplier, Product

class SupplierForm(forms.ModelForm):
    user_email = forms.EmailField()  # Campo de email del usuario
    user_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False  # No requerido, solo si desean cambiar la contraseña
    )

    class Meta:
        model = Supplier
        fields = ['supplier_name', 'supplier_address', 'supplier_state', 'supplier_city', 'supplier_zip_code']
        from django import forms
        
        
from django import forms
from .models import DatosRetiro

class EditarRetiroForm(forms.ModelForm):
    class Meta:
        model = DatosRetiro
        fields = ['nombre_titular', 'cuenta_paypal']  # Ajusta según los campos del modelo
        widgets = {
            'nombre_titular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Titular'}),
            'cuenta_paypal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Cuenta de PayPal'}),
        }

from django import forms
from django.contrib.auth.models import User

class ActualizarDatosForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AgregarProductoForm(forms.ModelForm):
    class Meta:
        model= Product
        fields = ['product_name', 'product_description', 'product_price', 'product_stock', 'product_image', 'product_width', 'product_height', 'product_thickness', 'product_material']
