# Generated by Django 3.2.8 on 2022-06-10 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_statictranslation_statictranslationtranslation'),
    ]

    operations = [
        migrations.AddField(
            model_name='estate',
            name='rating_average',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='estate',
            name='estate_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estates', to='api.estatetype', verbose_name='Тип недвижимости'),
        ),
    ]
