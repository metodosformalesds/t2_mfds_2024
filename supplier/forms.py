from django import forms
from product.models import Supplier, Product, SupplierPaymentMethodModel

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

class SupplierPaymentMethodForm(forms.ModelForm):
    class Meta:
        model = SupplierPaymentMethodModel
        fields = ['supplier_payment_method', 'supplier_payment_email', 'supplier_payment_name']
        labels = {
            'supplier_payment_method': 'Payment Method',
            'supplier_payment_email': 'PayPal Email',
            'supplier_payment_name': 'PayPal Account Name'
        }

from django import forms
from django.contrib.auth.models import User

class ActualizarDatosForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']




class AgregarProductoForm(forms.ModelForm):
    MATERIAL_CHOICES = [
        ('Metal', 'Metal'),
        ('Acero', 'Acero'),
        ('Aluminio', 'Aluminio'),
        ('Bronce', 'Bronce'),
    ]

    product_material = forms.ChoiceField(
        choices=MATERIAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control cantidad'})
    )
    
    class Meta:
        model = Product
        fields = [
            'product_name', 'product_description', 'product_price', 'product_stock',
            'product_image', 'product_width', 'product_height', 'product_thickness', 'product_material'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control cantidad'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control cantidad', 'rows': 1}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_stock': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control cantidad'}),
            'product_width': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_height': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_thickness': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
        }
        labels = {
            'product_name': 'Nombre del Producto',
            'product_description': 'Descripción del Producto',
            'product_price': 'Precio',
            'product_stock': 'Cantidad en Inventario',
            'product_image': 'Imagen del Producto',
            'product_width': 'Ancho del Producto',
            'product_height': 'Alto del Producto',
            'product_thickness': 'Grosor del Producto',
            'product_material': 'Material del Producto',
        }

    def clean_product_name(self):
        name = self.cleaned_data.get('product_name')
        if len(name) > 50:
            raise forms.ValidationError("El nombre del producto no puede tener más de 50 caracteres.")
        return name

    def clean_product_description(self):
        description = self.cleaned_data.get('product_description')
        if len(description) > 100:
            raise forms.ValidationError("La descripción debe ser menor a 100 caracteres.")
        return description

    def clean_product_price(self):
        price = self.cleaned_data.get('product_price')
        if price <= 0 or price > 9999:
            raise forms.ValidationError("El precio debe ser mayor a 0 y no exceder 9999.")
        return price

    def clean_product_stock(self):
        stock = self.cleaned_data.get('product_stock')
        if stock <= 0 or stock > 9999:
            raise forms.ValidationError("La cantidad en inventario debe ser mayor a 0 y no exceder 9999.")
        return stock

    def clean_product_width(self):
        width = self.cleaned_data.get('product_width')
        if width < 0.01 or width > 9999:
            raise forms.ValidationError("El ancho debe ser al menos 0.01 y no exceder 9999.")
        return width

    def clean_product_height(self):
        height = self.cleaned_data.get('product_height')
        if height < 0.01 or height > 9999:
            raise forms.ValidationError("El alto debe ser al menos 0.01 y no exceder 9999.")
        return height

    def clean_product_thickness(self):
        thickness = self.cleaned_data.get('product_thickness')
        if thickness < 0.01 or thickness > 9999:
            raise forms.ValidationError("El grosor debe ser al menos 0.01 y no exceder 9999.")
        return thickness

    def clean_product_image(self):
        image = self.cleaned_data.get('product_image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("Solo se permiten archivos de imagen JPG y PNG.")
        return image

class ActualizarProductosForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_price','product_stock']