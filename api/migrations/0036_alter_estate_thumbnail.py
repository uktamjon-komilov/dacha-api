# Generated by Django 3.2.9 on 2022-04-06 03:10

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20220405_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estate',
            name='thumbnail',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='jpeg', keep_meta=False, null=True, quality=100, size=[1000, 600], upload_to='images', verbose_name='Миниатюра'),
        ),
    ]