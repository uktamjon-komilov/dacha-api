# Generated by Django 3.2.7 on 2021-10-15 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20211015_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='estate',
            name='price_type',
            field=models.CharField(choices=[('som', "So'm"), ('usd', 'USD')], default='som', max_length=50),
        ),
    ]