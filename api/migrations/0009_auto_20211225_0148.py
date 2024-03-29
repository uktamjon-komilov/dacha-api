# Generated by Django 3.2.8 on 2021-12-25 01:48

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_estate_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='estatebanner',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='estate',
            name='photo',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='png', keep_meta=True, quality=20, size=[500, 300], upload_to='images'),
        ),
        migrations.AlterField(
            model_name='estatephoto',
            name='photo',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='png', keep_meta=True, quality=20, size=[500, 300], upload_to='images'),
        ),
    ]
