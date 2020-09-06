# from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from users.models import CustomUser, Photometer, Institution


def user_directory_path_measurements(instance, filename):
    return f'observation_files/{instance.id}.{filename.split(".")[-1]}'


class Observation(models.Model):

    #Id (primary key)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)

    #ForeignKeys
    author = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    photometer = models.ForeignKey(Photometer, on_delete=models.PROTECT)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, default='24f2bd47-c66a-4633-9234-d4b9108b98ae')

    # Date attributes
    date = models.DateTimeField(default=timezone.now)

    # Location attributes
    # latitude = models.DecimalField(max_digits=8, decimal_places=5, default=99.0)
    # longitude = models.DecimalField(max_digits=8, decimal_places=5, default=99.0)
    location = models.CharField(max_length=250, default = 'Nowhere')
    region = models.CharField(max_length=250, default = 'Noplace')
    state = models.CharField(max_length=250, default = 'Noneland')
    gispoint = models.PointField(geography=True, default=Point(0.0, 0.0))
    place = models.CharField(max_length=250, default='Somewhere', help_text='Place where measurements were taken.') # Users defined place

    publish = models.DateTimeField(default=timezone.now)

    # Weather attributes
    temperature = models.DecimalField(max_digits=6, decimal_places=3, default = 99.000)
    humidity = models.DecimalField(max_digits=6, decimal_places=3, blank=False, default = 99.0, help_text='Air humidity. If no value were recorded during measurements, pleas leave it as it is.')

    # Measurements attributes
    measurements_file = models.FileField(upload_to=user_directory_path_measurements, help_text="forms .txt file with measurements. Be sure this file was not edited after it's creation by the app")

    # image = models.FileField(upload_to=user_directory_path_image, blank=True)

    # Comments attributes
    comments = models.TextField(max_length=2000, default='No comments on this site', help_text="Any comments on this site e. g. 'there were clous', 'easy acces' or anything remarkable.")

    # Additional attributes
    # slug = models.SlugField(max_length=250, unique_for_date='publish', default='no-slug')

    class Meta:
        ordering = ('-publish',)


    def __str__(self):
        return f'Observation {self.location} by {self.author.username}'


class Measurement(models.Model):

    observation = models.ForeignKey(Observation, on_delete = models.CASCADE)
    index = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    T_IR = models.DecimalField(max_digits=7, decimal_places = 3, default=999.0, null = True)
    T_sensor = models.DecimalField(max_digits=7, decimal_places = 3, default=999.0, null = True)
    mag_value = models.DecimalField(max_digits=7, decimal_places = 3, default=999.0)
    hz = models.DecimalField(max_digits=7, decimal_places = 3, default=999.0, null = True)
    elevation = models.DecimalField(max_digits=7, decimal_places = 3, default=999.0)
    azimuth = models.DecimalField(max_digits=7, decimal_places = 3, default=999.0)
    latitude = models.DecimalField(max_digits=10, decimal_places = 3, default=999.0)
    longitude = models.DecimalField(max_digits=10, decimal_places = 3, default=999.0)
    sl = models.IntegerField(default=999, null = True)
    interpolated = models.BooleanField(default = False)

    def __str__(self):
        return f'{self.observation} number={self.index} interpolated={self.interpolated} id={self.observation.id}'


class KocijafBara(models.Model):

    """
    4-sources Kocijaf-Bara fitting parameters for each map
    """
    observation = models.ForeignKey(Observation, on_delete = models.CASCADE)

    #
    g = models.DecimalField(max_digits = 3, decimal_places = 2)
    t = models.DecimalField(max_digits = 3, decimal_places = 2)

    # Azimuths
    s1 = models.DecimalField(max_digits = 6, decimal_places = 5)
    s2 = models.DecimalField(max_digits = 6, decimal_places = 5)
    s3 = models.DecimalField(max_digits = 6, decimal_places = 5)
    s4 = models.DecimalField(max_digits = 6, decimal_places = 5)

    l1 = models.DecimalField(max_digits = 7, decimal_places = 5)
    l2 = models.DecimalField(max_digits = 7, decimal_places = 5)
    l3 = models.DecimalField(max_digits = 7, decimal_places = 5)
    l4 = models.DecimalField(max_digits = 7, decimal_places = 5)

    time_spent = models.DecimalField(max_digits = 5, decimal_places = 3, default = 10)



# This is an auto-generated Django model module created by ogrinspect.

class WorldBorder(models.Model):
    fips = models.CharField(max_length=2)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    un = models.IntegerField()
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.BigIntegerField()
    region = models.IntegerField()
    subregion = models.IntegerField()
    lon = models.FloatField()
    lat = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)


# Auto-generated `LayerMapping` dictionary for WorldBorder model
worldborder_mapping = {
    'fips': 'FIPS',
    'iso2': 'ISO2',
    'iso3': 'ISO3',
    'un': 'UN',
    'name': 'NAME',
    'area': 'AREA',
    'pop2005': 'POP2005',
    'region': 'REGION',
    'subregion': 'SUBREGION',
    'lon': 'LON',
    'lat': 'LAT',
    'geom': 'MULTIPOLYGON',
}



