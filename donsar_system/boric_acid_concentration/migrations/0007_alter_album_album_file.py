# Generated by Django 4.0.3 on 2022-03-24 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boric_acid_concentration', '0006_borcalculator_param_2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='album_file',
            field=models.FileField(upload_to='albums/', verbose_name='Альбом'),
        ),
    ]
