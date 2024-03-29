# Generated by Django 3.2.8 on 2021-11-25 16:17

import api.models
import api.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.fields
import parler.fields
import parler.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(max_length=25, unique=True, verbose_name='Telefon raqam')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Ismi')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Familiyasi')),
                ('photo', models.FileField(blank=True, null=True, upload_to='user/')),
                ('balance', models.FloatField(default=0.0)),
                ('is_staff', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdvertisingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('days', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Estate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', sorl.thumbnail.fields.ImageField(upload_to='')),
                ('beds', models.IntegerField(blank=True, default=0)),
                ('pool', models.IntegerField(blank=True, default=0)),
                ('people', models.IntegerField(blank=True, default=0)),
                ('weekday_price', models.FloatField(verbose_name='Begim kunlaridagi narxi')),
                ('weekend_price', models.FloatField(verbose_name='Dam olish kunlari narxi')),
                ('address', models.CharField(max_length=255, verbose_name='Manzil')),
                ('longtitute', models.FloatField(blank=True, null=True, verbose_name='Longtitute')),
                ('latitute', models.FloatField(blank=True, null=True, verbose_name='Latitute')),
                ('announcer', models.CharField(max_length=255, verbose_name="E'lon beruvchi")),
                ('phone', models.CharField(max_length=20, verbose_name='Telefon raqam')),
                ('is_published', models.BooleanField(default=True, verbose_name='Chop etilishi')),
                ('expires_in', models.DateField(blank=True, null=True)),
                ('is_topbanner', models.BooleanField(blank=True, default=False, null=True)),
                ('is_banner', models.BooleanField(blank=True, default=False, null=True)),
                ('is_top', models.BooleanField(blank=True, default=False, null=True)),
                ('is_ads', models.BooleanField(blank=True, default=False, null=True)),
                ('is_simple', models.BooleanField(blank=True, default=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EstateFacility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EstateType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
                ('icon', models.FileField(blank=True, null=True, upload_to='icons/')),
                ('priority', models.IntegerField(default=1)),
                ('foreground_color', models.CharField(blank=True, max_length=8, null=True)),
                ('background_color', models.CharField(blank=True, max_length=8, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.FileField(upload_to='images/')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.estate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('estate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_messages', to='api.estate')),
                ('receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sender_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EstateViews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=255)),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='api.estate')),
            ],
            bases=(models.Model, api.models.DateTimeMixin),
        ),
        migrations.CreateModel(
            name='EstateRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='api.estate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, django.db.models.fields.DateTimeField),
        ),
        migrations.CreateModel(
            name='EstatePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.FileField(upload_to=api.utils.get_file_path)),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='api.estate')),
            ],
            bases=(models.Model, api.models.DateTimeMixin),
        ),
        migrations.CreateModel(
            name='EstateBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booked_days', to='api.estate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, api.models.DateTimeMixin),
        ),
        migrations.CreateModel(
            name='EstateBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField(default=30)),
                ('expires_in', models.DateField(blank=True, null=True)),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.estate')),
            ],
            bases=(models.Model, api.models.DateTimeMixin),
        ),
        migrations.AddField(
            model_name='estate',
            name='estate_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.estatetype', verbose_name='Mulk turi'),
        ),
        migrations.AddField(
            model_name='estate',
            name='facilities',
            field=models.ManyToManyField(blank=True, to='api.EstateFacility'),
        ),
        migrations.AddField(
            model_name='estate',
            name='price_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.currency'),
        ),
        migrations.AddField(
            model_name='estate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="E'lon beruvchi profili"),
        ),
        migrations.CreateModel(
            name='BalanceCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('in', 'IN'), ('out', 'OUT')], max_length=100)),
                ('completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StaticPageTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('content', models.TextField(verbose_name='Kontent')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.staticpage')),
            ],
            options={
                'verbose_name': 'static page Translation',
                'db_table': 'api_staticpage_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ServiceTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('content', models.TextField(verbose_name='Kontent')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.service')),
            ],
            options={
                'verbose_name': 'service Translation',
                'db_table': 'api_service_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EstateTypeTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.estatetype')),
            ],
            options={
                'verbose_name': 'estate type Translation',
                'db_table': 'api_estatetype_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EstateTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('description', models.TextField(verbose_name='Tavsif')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.estate')),
            ],
            options={
                'verbose_name': 'estate Translation',
                'db_table': 'api_estate_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EstateFacilityTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.estatefacility')),
            ],
            options={
                'verbose_name': 'estate facility Translation',
                'db_table': 'api_estatefacility_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CurrencyTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.currency')),
            ],
            options={
                'verbose_name': 'currency Translation',
                'db_table': 'api_currency_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AdvertisingPlanTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Nomi')),
                ('content', models.TextField(verbose_name='Kontent')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.advertisingplan')),
            ],
            options={
                'verbose_name': 'advertising plan Translation',
                'db_table': 'api_advertisingplan_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
