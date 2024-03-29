# Generated by Django 3.2.8 on 2022-01-04 18:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20211230_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='estate',
            name='beds',
            field=models.IntegerField(blank=True, default=5),
        ),
        migrations.AlterField(
            model_name='estate',
            name='people',
            field=models.IntegerField(blank=True, default=5),
        ),
        migrations.AlterField(
            model_name='estate',
            name='pool',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
