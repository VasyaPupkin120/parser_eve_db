# Generated by Django 5.0.2 on 2024-03-08 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_universe', '0009_stars'),
    ]

    operations = [
        migrations.AddField(
            model_name='stars',
            name='response_body',
            field=models.JSONField(null=True),
        ),
    ]