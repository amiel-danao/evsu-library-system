# Generated by Django 4.1.3 on 2023-02-02 06:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0017_alter_genre_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='book_price',
            field=models.FloatField(default=0, help_text='Student will be responsible to pay ₱{} if they lost the borrowed book', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='book',
            name='overtime_fine',
            field=models.FloatField(default=0, help_text='Student will be responsible to pay ₱{} if they exceeded the return date', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unpaid_penalty', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('book_borrowed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.book')),
                ('borrower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.student')),
            ],
            options={
                'verbose_name_plural': 'Penalties',
            },
        ),
    ]