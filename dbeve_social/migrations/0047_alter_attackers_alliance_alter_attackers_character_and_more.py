# Generated by Django 5.0.2 on 2024-05-07 16:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_items', '0007_alter_types_mass'),
        ('dbeve_social', '0046_alter_victims_killmail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attackers',
            name='alliance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dbeve_social.alliances'),
        ),
        migrations.AlterField(
            model_name='attackers',
            name='character',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dbeve_social.characters'),
        ),
        migrations.AlterField(
            model_name='attackers',
            name='corporation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dbeve_social.corporations'),
        ),
        migrations.AlterField(
            model_name='attackers',
            name='ship',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attackers_ship_type', to='dbeve_items.types'),
        ),
        migrations.AlterField(
            model_name='attackers',
            name='weapon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attackers_weapon_type', to='dbeve_items.types'),
        ),
        migrations.AlterField(
            model_name='victims',
            name='alliance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dbeve_social.alliances'),
        ),
        migrations.AlterField(
            model_name='victims',
            name='character',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dbeve_social.characters'),
        ),
        migrations.AlterField(
            model_name='victims',
            name='corporation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dbeve_social.corporations'),
        ),
        migrations.AlterField(
            model_name='victims',
            name='ship',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dbeve_items.types'),
        ),
    ]
