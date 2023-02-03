# Generated by Django 4.1.3 on 2023-02-02 12:44

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0023_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='inventory_stock',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(default='', max_length=255, verbose_name='Book Title'),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='date_borrowed',
            field=models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='Date of Book Issuance'),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='return_date',
            field=models.DateField(default=django.utils.timezone.now, help_text='The system automatically set the min number of day of borrowing book in to 3 days.', verbose_name='Date of Returning Book'),
            preserve_default=False,
        ),
    ]