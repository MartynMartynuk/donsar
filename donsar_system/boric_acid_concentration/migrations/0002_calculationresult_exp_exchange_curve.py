# Generated by Django 4.0.3 on 2022-05-29 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boric_acid_concentration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculationresult',
            name='exp_exchange_curve',
            field=models.JSONField(null=True),
        ),
    ]
