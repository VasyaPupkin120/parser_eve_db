# Generated by Django 5.0.2 on 2024-04-30 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_social', '0030_rename_ship_type_killmails_victim_ship_type_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='killmails',
            old_name='victim_allinace',
            new_name='victim_alliance',
        ),
    ]