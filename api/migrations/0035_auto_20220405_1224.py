# Generated by Django 3.2.9 on 2022-04-05 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_alter_user_fcm_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='estate',
            name='is_ads_plus',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Реклама+'),
        ),
        migrations.DeleteModel(
            name='EstateBanner',
        ),
    ]