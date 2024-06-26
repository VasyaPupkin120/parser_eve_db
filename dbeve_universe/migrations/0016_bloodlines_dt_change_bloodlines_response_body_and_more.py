# Generated by Django 5.0.2 on 2024-04-22 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_universe', '0015_constellations_dt_change_regions_dt_change_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloodlines',
            name='dt_change',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='bloodlines',
            name='response_body',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='factions',
            name='dt_change',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='factions',
            name='response_body',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='dt_change',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='response_body',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='stations',
            name='dt_change',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='stations',
            name='response_body',
            field=models.JSONField(null=True),
        ),
    ]
