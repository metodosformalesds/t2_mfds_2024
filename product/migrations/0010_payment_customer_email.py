# Generated by Django 4.2.3 on 2024-11-13 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_remove_supplierpaymentmethodmodel_supplier_method_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
