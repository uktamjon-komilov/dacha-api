# Generated by Django 3.2.8 on 2022-03-14 02:34

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20220314_0230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estate',
            name='photo',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='jpeg', keep_meta=False, quality=100, size=[3000, 1800], upload_to='images'),
        ),
    ]
