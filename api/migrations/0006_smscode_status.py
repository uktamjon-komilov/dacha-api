# Generated by Django 3.2.7 on 2021-10-08 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20211008_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='smscode',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
