# Generated by Django 3.2.7 on 2021-10-15 06:07

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_smscode_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstateBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField(default=30)),
                ('expires_in', models.DateTimeField(blank=True, null=True)),
            ],
            bases=(models.Model, api.models.DateTimeMixin),
        ),
        migrations.DeleteModel(
            name='SmsCode',
        ),
        migrations.AddField(
            model_name='estate',
            name='expires_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='estatebanner',
            name='estate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.estate'),
        ),
    ]