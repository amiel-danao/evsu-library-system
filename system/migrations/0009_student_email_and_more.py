# Generated by Django 4.1.3 on 2023-01-15 14:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0008_student_first_name_student_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(default='', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='incomingtransaction',
            name='date_returned',
            field=models.DateField(blank=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='date_borrowed',
            field=models.DateField(blank=True, default=django.utils.timezone.now),
        ),
    ]
