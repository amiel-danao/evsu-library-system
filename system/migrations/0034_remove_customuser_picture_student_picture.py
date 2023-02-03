# Generated by Django 4.1.3 on 2023-02-03 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0033_outgoingtransaction_returned'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='picture',
        ),
        migrations.AddField(
            model_name='student',
            name='picture',
            field=models.ImageField(blank=True, default='', null=True, upload_to='images/'),
        ),
    ]
