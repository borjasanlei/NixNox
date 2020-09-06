# Generated by Django 3.0.8 on 2020-08-07 08:29

import allskymaps.models
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.PositiveIntegerField(default=0)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('T_IR', models.DecimalField(decimal_places=3, default=99.0, max_digits=7, null=True)),
                ('T_sensor', models.DecimalField(decimal_places=3, default=99.0, max_digits=7, null=True)),
                ('mag_value', models.DecimalField(decimal_places=3, default=99.0, max_digits=6)),
                ('hz', models.DecimalField(decimal_places=3, default=99.0, max_digits=6, null=True)),
                ('altitude', models.DecimalField(decimal_places=3, default=99.0, max_digits=6)),
                ('azimuth', models.DecimalField(decimal_places=3, default=99.0, max_digits=6)),
                ('latitude', models.DecimalField(decimal_places=3, default=99.0, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=3, default=99.0, max_digits=10)),
                ('sl', models.IntegerField(default=99, null=True)),
                ('interpolated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('latitude', models.DecimalField(decimal_places=5, default=99.0, max_digits=8)),
                ('longitude', models.DecimalField(decimal_places=5, default=99.0, max_digits=8)),
                ('location', models.CharField(default='Nowhere', max_length=250)),
                ('state', models.CharField(default='Noneland', max_length=250)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
                ('temperature', models.DecimalField(decimal_places=3, default=99.0, max_digits=6)),
                ('humidity', models.DecimalField(decimal_places=3, default=99.0, max_digits=6)),
                ('measurements_file', models.FileField(upload_to=allskymaps.models.user_directory_path_measurements)),
                ('comments', models.TextField(default='No comments on this site', max_length=2000)),
            ],
            options={
                'ordering': ('-publish',),
            },
        ),
    ]
