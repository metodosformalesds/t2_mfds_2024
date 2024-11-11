from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


# Create your models here.
 
from django.db import models
 
# Clases para inizializar las opciones pre-establecidas
class UserRole(models.TextChoices):
    SUPPLIER = 'Supplier', 'Supplier'
    CLIENT = 'Client', 'Client'

class UserAuthProvider(models.TextChoices):
    INTERNAL = 'Internal', 'Internal'
    FACEBOOK = 'Facebook', 'Facebook'
    IOS = 'iOS', 'iOS'

class PaymentMethod(models.TextChoices):
    STRIPE = 'Stripe', 'Stripe'
    PAYPAL = 'Paypal', 'Paypal'

class PaymentStatus(models.TextChoices):
    COMPLETED = 'Completed', 'Completed'
    PENDING = 'Pending', 'Pending'
    FAILED = 'Failed', 'Failed'

class SupplierPaymentMethod(models.TextChoices):
    PAYPAL = 'Paypal', 'Paypal'
    STRIPE = 'Stripe', 'Stripe'
 
 
 
class UserAccount(models.Model):
    id_user = models.AutoField(primary_key=True)
    user_email = models.EmailField(max_length=255, unique=True)
    user_password = models.CharField(max_length=255, null=True, blank=True)
    user_role = models.CharField(max_length=20, choices=UserRole.choices)
    user_auth_provider = models.CharField(max_length=20, choices=UserAuthProvider.choices, default=UserAuthProvider.INTERNAL)
    user_auth_provider_id = models.CharField(max_length=255, null=True, blank=True)
    
    def set_password(self, raw_password):
        """Establecer la contraseña encriptada."""
        self.user_password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verificar la contraseña."""
        return check_password(raw_password, self.user_password)
    
    def __str__(self):
        return self.user_email
 
 
class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    balance = models.FloatField(default=0.0) 
    supplier_name = models.CharField(max_length=50)
    supplier_rating = models.FloatField(default=0)
    supplier_address = models.CharField(max_length=100)
    supplier_state = models.CharField(max_length=50)
    supplier_city = models.CharField(max_length=50)
    supplier_zip_code = models.CharField(max_length=10)
    # Aquí aplicamos el filtro para que solo se muestren los usuarios con rol 'Supplier'
    
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE,limit_choices_to={'user_role': UserRole.SUPPLIER}) 
    def __str__(self):
        return self.supplier_name
 
 
 
class Client(models.Model):
    id_client = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, limit_choices_to={'user_role': UserRole.CLIENT})
    client_first_name = models.CharField(max_length=50)
    client_last_name = models.CharField(max_length=50)
    client_phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.client_first_name} {self.client_last_name}"
 
 
 
class ClientAddress(models.Model):
    id_address = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    client_address = models.CharField(max_length=100)
    client_city = models.CharField(max_length=50)
    client_state = models.CharField(max_length=50)
    client_zip_code = models.IntegerField()
    client_address_additional_information = models.CharField(max_length=150)
 
    def __str__(self):
        return self.client_address
 
 
 
class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_description = models.CharField(max_length=100)
    product_price = models.IntegerField(default=0) #Centavos
    product_stock = models.IntegerField(default=0)
    product_image = models.ImageField(("Product Image"), upload_to='media/products_images/', null=False)
    product_width = models.FloatField(default=0)
    product_height = models.FloatField(default=0)
    product_thickness = models.FloatField(default=0)
    product_material = models.CharField(max_length=50)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
 
    def __str__(self):
        return self.product_name
    
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
 
 
class Order(models.Model):
    id_order = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.ForeignKey(ClientAddress, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
 
    def __str__(self):
        return f"Order {self.id_order}"
 
 
 
class OrderItem(models.Model):
    id_order_item = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_purchase = models.FloatField()
 
    def __str__(self):
        return f"Order Item {self.id_order_item}"
 
 
 
class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipment_tracking_number = models.CharField(max_length=50)
    shipment_carrier = models.CharField(max_length=50)
    shipment_status = models.CharField(max_length=50)
    shipment_date = models.DateTimeField()
    shipment_estimated_delivery_date = models.DateTimeField()
    shipment_actual_delivery_date = models.DateTimeField()
 
    def __str__(self):
        return f"Shipment {self.id_shipment}"
 
 
 
class Payment(models.Model):
    id_payment = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices)

    app_user = models.ForeignKey(Client, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
 
    def __str__(self):
        return f"Payment {self.id_payment}"
 
 
class ShoppingCart(models.Model):
    id_cart = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_product_quantity = models.IntegerField(default=1)
    cart_added_date = models.DateTimeField()
 
    def __str__(self):
        return f"Cart {self.id_cart}"
 
 
 
class WishItem(models.Model):
    id_wish = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    wish_date_added = models.DateTimeField()
 
    def __str__(self):
        return f"Wish {self.id_wish}"
 
 
class PasswordReset(models.Model):
    id_reset = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=10)
    reset_expiration_time = models.DateTimeField()
 
    def __str__(self):
        return f"Password Reset {self.id_reset}"
 
 
 
class SupplierPaymentMethodModel(models.Model):
    id_supplier_payment = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payment_methods')
    supplier_method_id = models.CharField(max_length=255)
    supplier_payment_method = models.CharField(
    max_length=20,
    choices=SupplierPaymentMethod.choices  # Usar así para las opciones del campo
)
    supplier_payment_email = models.CharField(max_length=50)

    def __str__(self):
        return f"Supplier Payment {self.id_supplier_payment}"
 
 
 
class SupplierSales(models.Model):
    Supplier_order_sales = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    total_sales = models.FloatField(default=0)
 
    def __str__(self):
        return f"Supplier Sales {self.Supplier_order_sales}"
 
 
 
class Recycle(models.Model):
    id_recycle = models.AutoField(primary_key=True)
    recycle_name = models.CharField(max_length=255)
    recycle_image = models.ImageField(("Recycle Image"), upload_to='static/products_images/', null=False)
    recycle_description = models.CharField(max_length=255)
    recycle_address = models.CharField(max_length=255)
    recycle_number = models.CharField(max_length=20)
    
 
    def __str__(self):
        return self.recycle_name