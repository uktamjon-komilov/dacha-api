# Generated by Django 3.2.8 on 2022-02-28 17:26

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20220216_0359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estate',
            name='photo',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='png', keep_meta=True, quality=100, size=[1500, 900], upload_to='images'),
        ),
        migrations.AlterField(
            model_name='estatephoto',
            name='photo',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='png', keep_meta=True, quality=100, size=[1500, 900], upload_to='images'),
        ),
    ]
