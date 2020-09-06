# Generated by Django 3.1 on 2020-08-09 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allskymaps', '0006_auto_20200808_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='T_IR',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='T_sensor',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='altitude',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='azimuth',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='hz',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='latitude',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='longitude',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='mag_value',
            field=models.DecimalField(decimal_places=3, default=999.0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='sl',
            field=models.IntegerField(default=999, null=True),
        ),
    ]
