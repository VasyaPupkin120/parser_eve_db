# Generated by Django 5.0.2 on 2024-05-04 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_social', '0041_attackers_dt_change_attackers_response_body_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='victimitems',
            name='item_type',
        ),
        migrations.RemoveField(
            model_name='victimitems',
            name='victim',
        ),
        migrations.RemoveField(
            model_name='victims',
            name='alliance',
        ),
        migrations.RemoveField(
            model_name='victims',
            name='character',
        ),
        migrations.RemoveField(
            model_name='victims',
            name='corporation',
        ),
        migrations.RemoveField(
            model_name='victims',
            name='killmail',
        ),
        migrations.RemoveField(
            model_name='victims',
            name='ship',
        ),
        migrations.DeleteModel(
            name='Attackers',
        ),
        migrations.DeleteModel(
            name='VictimItems',
        ),
        migrations.DeleteModel(
            name='Victims',
        ),
    ]
