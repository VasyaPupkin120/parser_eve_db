# Generated by Django 5.0.2 on 2024-05-01 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_social', '0033_alter_killmails_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='killmails',
            options={'ordering': ['victim_alliance', 'victim_corporation', '-sumv']},
        ),
    ]