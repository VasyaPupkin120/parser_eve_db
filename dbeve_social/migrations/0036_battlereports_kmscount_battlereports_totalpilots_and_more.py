# Generated by Django 5.0.2 on 2024-05-02 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_social', '0035_battlereports_delete_relates'),
    ]

    operations = [
        migrations.AddField(
            model_name='battlereports',
            name='kmsCount',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='battlereports',
            name='totalPilots',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='battlereports',
            name='totalShips',
            field=models.BigIntegerField(null=True),
        ),
    ]
