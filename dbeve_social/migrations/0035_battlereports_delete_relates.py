# Generated by Django 5.0.2 on 2024-05-02 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbeve_social', '0034_alter_killmails_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battlereports',
            fields=[
                ('dt_change', models.DateTimeField(auto_now=True, null=True)),
                ('response_body', models.JSONField(null=True)),
                ('battlereport_id', models.CharField(primary_key=True, serialize=False)),
                ('url', models.URLField(null=True)),
                ('killmails', models.ManyToManyField(blank=True, related_name='battlereports', to='dbeve_social.killmails')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Relates',
        ),
    ]
