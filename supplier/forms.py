from django import forms
from product.models import Supplier

class SupplierForm(forms.ModelForm):
    user_email = forms.EmailField()
    user_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False
    )
    user_first_name = forms.CharField()
    user_last_name = forms.CharField()
    user_last_second_name = forms.CharField()

    class Meta:
        model = Supplier
        fields = ['supplier_name', 'supplier_address', 'supplier_state', 'supplier_city', 'supplier_zip_code']
