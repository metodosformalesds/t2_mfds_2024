# Generated by Django 4.2.3 on 2024-11-12 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_remove_payment_order_alter_payment_payment_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplierpaymentmethodmodel',
            name='supplier_method_id',
        ),
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='product.order'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='balance',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='supplierpaymentmethodmodel',
            name='supplier_payment_name',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clientaddress',
            name='client_address_additional_information',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='clientaddress',
            name='client_zip_code',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='supplierpaymentmethodmodel',
            name='supplier',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='product.supplier'),
        ),
        migrations.AlterField(
            model_name='supplierpaymentmethodmodel',
            name='supplier_payment_email',
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name='supplierpaymentmethodmodel',
            name='supplier_payment_method',
            field=models.CharField(choices=[('PayPal', 'PayPal')], max_length=20),
        ),
        migrations.AlterField(
            model_name='suppliersales',
            name='supplier',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='product.supplier'),
        ),
    ]