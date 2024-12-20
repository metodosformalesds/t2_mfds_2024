# Generated by Django 4.2.3 on 2024-11-09 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_client_user_alter_supplier_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='app_user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='product.client'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_bool',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_checkout_id',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='product_price',
            field=models.IntegerField(default=0),
        ),
    ]
