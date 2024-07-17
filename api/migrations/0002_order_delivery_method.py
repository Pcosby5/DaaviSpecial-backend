# Generated by Django 5.0.6 on 2024-07-16 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(choices=[('Delivery', 'Delivery'), ('Postal', 'Postal'), ('Pickup', 'Pickup')], default='Delivery', max_length=50),
        ),
    ]
