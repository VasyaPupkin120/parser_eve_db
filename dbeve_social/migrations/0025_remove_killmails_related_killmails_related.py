# Generated by Django 5.0.2 on 2024-04-26 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_social', '0024_rename_relate_id_relates_related_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='killmails',
            name='related',
        ),
        migrations.AddField(
            model_name='killmails',
            name='related',
            field=models.ManyToManyField(to='dbeve_social.relates'),
        ),
    ]
