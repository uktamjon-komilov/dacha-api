# Generated by Django 3.2.8 on 2021-12-30 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_message_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='email',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='phone1',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='phone2',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]