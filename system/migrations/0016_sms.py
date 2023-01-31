# Generated by Django 4.1.3 on 2023-01-25 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0015_alter_student_mobile_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=150)),
                ('students', models.ManyToManyField(to='system.student')),
            ],
        ),
    ]
