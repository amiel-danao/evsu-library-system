# Generated by Django 4.1.3 on 2023-02-02 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0027_alter_book_isbn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingtransaction',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.book'),
        ),
        migrations.AlterField(
            model_name='outgoingtransaction',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.book'),
        ),
    ]
