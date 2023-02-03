# Generated by Django 4.1.3 on 2023-02-02 13:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0025_remove_book_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='inventory_stock',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
