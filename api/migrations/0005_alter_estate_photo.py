# Generated by Django 3.2.8 on 2021-12-22 21:04

from django.db import migrations
import smartfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20211221_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estate',
            name='photo',
            field=smartfields.fields.ImageField(upload_to=''),
        ),
    ]
