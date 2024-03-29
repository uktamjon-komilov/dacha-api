# Generated by Django 3.2.9 on 2022-04-06 04:46

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_alter_estate_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='thumbnail',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='jpeg', keep_meta=False, null=True, quality=100, size=[200, 200], upload_to='images', verbose_name='Миниатюра'),
        ),
    ]
