from django.shortcuts import render, redirect
from django.contrib import messages
from product.models import Supplier, UserAccount  # Importamos los modelos
from django import forms

# Creamos un formulario básico usando Django Forms
class SupplierRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Supplier
        fields = ['supplier_name', 'supplier_address', 'supplier_city', 'supplier_zip_code', 'supplier_state']

    def save(self, commit=True):
        # Creamos primero un nuevo usuario (UserAccount)
        user = UserAccount(
            user_email=self.cleaned_data['email'],
            user_password=self.cleaned_data['password']  # Debes encriptar la contraseña después
        )
        if commit:
            user.save()

        # Guardamos la información del proveedor (Supplier)
        supplier = super(SupplierRegisterForm, self).save(commit=False)
        supplier.user = user
        if commit:
            supplier.save()
        return supplier

# Definimos la vista para manejar el registro
def supplier_register(request):
    if request.method == 'POST':
        form = SupplierRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor registrado exitosamente')
            return redirect('supplier_login')  # Redirige a la página de inicio de sesión o donde prefieras
    else:
        form = SupplierRegisterForm()

    return render(request, 'home/supplier_register.html', {'form': form})


# Create your views here.
def register(request):
    return render(request, 'home/register.html')
