# Generated by Django 4.2.3 on 2024-11-04 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_alter_product_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.ForeignKey(limit_choices_to={'user_role': 'Client'}, on_delete=django.db.models.deletion.CASCADE, to='product.useraccount'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='user',
            field=models.ForeignKey(limit_choices_to={'user_role': 'Supplier'}, on_delete=django.db.models.deletion.CASCADE, to='product.useraccount'),
        ),
    ]
