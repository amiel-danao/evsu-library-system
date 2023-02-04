# Generated by Django 4.1.3 on 2023-02-03 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0034_remove_customuser_picture_student_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='picture',
            field=models.ImageField(blank=True, default='', null=True, upload_to='books_images/'),
        ),
        migrations.AlterUniqueTogether(
            name='outgoingtransaction',
            unique_together={('book', 'borrower', 'returned')},
        ),
    ]