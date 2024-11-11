from django import forms
from product.models import Client, ClientAddress

class ClientForm(forms.ModelForm):
    user_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo'})
    )
    user_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}),
        required=False
    )
    client_first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    client_last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    client_phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = Client
        fields = ['client_first_name', 'client_last_name', 'client_phone']


class ClientAddressForm(forms.ModelForm):
    class Meta:
        model = ClientAddress
        fields = ['client_address', 'client_city', 'client_state', 'client_zip_code', 'client_address_additional_information']
        widgets = {
            'client_address': forms.TextInput(attrs={'class': 'form-control cantidad', 'placeholder': 'Ingrese la dirección'}),
            'client_city': forms.TextInput(attrs={'class': 'form-control cantidad', 'placeholder': 'Ingrese la ciudad'}),
            'client_state': forms.TextInput(attrs={'class': 'form-control cantidad', 'placeholder': 'Ingrese el estado'}),
            'client_zip_code': forms.NumberInput(attrs={'class': 'form-control cantidad', 'placeholder': 'Ingrese el código postal'}),
            'client_address_additional_information': forms.TextInput(attrs={'class': 'form-control cantidad', 'placeholder': 'Información adicional'}),
        }
