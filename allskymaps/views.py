from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
import pandas as pd
import numpy as np
from astropy.table import Table
from djqscsv import write_csv
import random
import string

from sqlalchemy import create_engine

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent = 'nixnox')

from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from celery.decorators import task


from .forms import TASObservationForm, NixnoxPyForm, QueryPointForm
from .backend import TASObs, NixnoxPy
from .models import Measurement, Observation, KocijafBara
from .AnalysisToolkit import complete_analysis

@task(name = "pandas_sql_tas")
def pandas_sql_tas(data, TAS_instance, alt, azi, mag):
    data_table = data.to_pandas()
    data_table['Datetime'] = data['Datetime'].datetime

    data_table['observation'] = TAS_instance.id

    data_table.columns = ['index', 'date', 'T_IR', 'T_sensor', 'mag_value', 'hz', 'elevation', 'azimuth',
                          'latitude', 'longitude', 'sl', 'observation_id']
    data_table['interpolated'] = False

    db_connection_url = "postgresql://{}:{}@{}:{}/{}".format(
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'],
        settings.DATABASES['default']['HOST'],
        settings.DATABASES['default']['PORT'],
        settings.DATABASES['default']['NAME'],
    )

    engine = create_engine(db_connection_url)

    data_table.to_sql(Measurement._meta.db_table, engine, if_exists = 'append', index = False, chunksize = 10000)

    alt = np.reshape(alt, -1)
    azi = np.reshape(azi, -1)
    mag = np.reshape(mag, -1)

    df_interpolated = pd.DataFrame({'elevation': alt, 'azimuth': azi, 'mag_value': mag}).dropna()
    df_interpolated['observation_id'] = TAS_instance.id
    df_interpolated['date'] = data_table['date'][0]
    df_interpolated['interpolated'] = True
    df_interpolated['latitude'] = np.mean(data['Lat'])
    df_interpolated['longitude'] = np.mean(data['Long'])
    df_interpolated['index'] = 999
    df_interpolated.to_sql(Measurement._meta.db_table, engine, if_exists = 'append', index = False, chunksize = 10000)
    #return data_table, df_interpolated


@task(name = "pandas_sql_py")
def pandas_sql_py(data, TAS_instance, alt, azi, mag):
    db_connection_url = "postgresql://{}:{}@{}:{}/{}".format(
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'],
        settings.DATABASES['default']['HOST'],
        settings.DATABASES['default']['PORT'],
        settings.DATABASES['default']['NAME'],
    )

    engine = create_engine(db_connection_url)

    data_table = data.to_pandas()

    data_table['Datetime'] = data['Datetime'].datetime

    data_table['observation'] = TAS_instance.id
    data_table.columns = ['elevation', 'mag_value', 'azimuth', 'latitude', 'longitude', 'index', 'date',
                          'T_IR',
                          'T_sensor',
                          'hz', 'sl', 'observation_id']
    data_table['interpolated'] = False
    data_table.to_sql(Measurement._meta.db_table, engine, if_exists = 'append', index = False,
                      chunksize = 10000)

    alt = np.reshape(alt, -1)
    azi = np.reshape(azi, -1)
    mag = np.reshape(mag, -1)

    df_interpolated = pd.DataFrame({'elevation': alt, 'azimuth': azi, 'mag_value': mag}).dropna()
    df_interpolated['observation_id'] = TAS_instance.id
    df_interpolated['date'] = data_table['date'][0]
    df_interpolated['interpolated'] = True
    df_interpolated['latitude'] = np.mean(data['Lat'])
    df_interpolated['longitude'] = np.mean(data['Long'])
    df_interpolated['index'] = 999
    df_interpolated.to_sql(Measurement._meta.db_table, engine, if_exists = 'append', index = False,
                           chunksize = 10000)


@task(name = "obs_analysis")
def obs_analysis(obsname):
    parameters, time_spent = complete_analysis(obsname = obsname)

    p_instance = KocijafBara()
    p_instance.g = parameters['g'].value
    p_instance.t = parameters['t'].value

    p_instance.s1 = parameters['s1'].value
    p_instance.s2 = parameters['s2'].value
    p_instance.s3 = parameters['s3'].value
    p_instance.s4 = parameters['s4'].value

    p_instance.l1 = parameters['l1'].value
    p_instance.l2 = parameters['l2'].value
    p_instance.l3 = parameters['l3'].value
    p_instance.l4 = parameters['l4'].value

    p_instance.time_spent = time_spent

    p_instance.observation_id = obsname
    p_instance.save()

    ecsv_file = Table.read(f'media/observation_files/{obsname}.ecsv', format='ascii.ecsv', delimiter=',')

    for name in parameters.keys():
        ecsv_file.meta[name] = parameters[name].value

    ecsv_file.meta['time_spent'] = time_spent
    ecsv_file.write(f'media/observation_files/{obsname}.ecsv', format='ascii.ecsv', delimiter=',', overwrite=True)




class TASFormView(View):

    template_name = 'forms/obs_form.html'
    form_class = TASObservationForm
    success_url = ''

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            values_view = request.FILES.values()
            value_iterator = iter(values_view)
            TAS_file = next(value_iterator)

            if TAS_file.size > 15000:
                return render(request, self.template_name, {'not_valid': True})

            else:

                TAS_instance = form.save()

                path = TAS_instance.measurements_file.path

                meta_dict = {
                    'author': TAS_instance.author.username,
                    'institution': TAS_instance.institution.name,
                    'photometer': TAS_instance.photometer.serial_id,
                    'place': TAS_instance.place,
                    'comments': TAS_instance.comments,
                }

                new_map = TASObs(path, meta_dict, name=TAS_instance.place)
                map_path, ecsv_path, data, mag, azi, alt, lat, long = new_map.pipeline()

                # Looks for the place
                location = geolocator.reverse(
                    f"{lat.to_string(decimal = True)}, {long.to_string(decimal = True)}",
                    exactly_one = True, zoom = 10)
                address = location.address.split(', ')

                area, province, ccaa = (address[0], address[1], address[2])
                ecsv_filename = ecsv_path.split('/')[-1]
                map_filename = map_path.split('/')[-1]

                TAS_instance.location = area
                TAS_instance.region = province
                TAS_instance.state = ccaa

                TAS_instance.gispoint = Point(np.mean(data['Long']), np.mean(data['Lat']))

                TAS_instance.date = data['Datetime'][0].datetime
                TAS_instance.save()

                obs_analysis.delay(f'{TAS_instance.id}')
                pandas_sql_tas.delay(data, TAS_instance, alt, azi, mag)

                return render(request, self.template_name, {'map_path': map_path.split('nixnox_project')[1],
                                                            'ecsv_path': ecsv_path.split('nixnox_project')[1],
                                                            'ecsv_filename': ecsv_filename,
                                                            'map_filename': map_filename,
                                                            'user':TAS_instance.author,
                                                            'lat':np.mean(data['Lat']),
                                                            'long':np.mean(data['Long']),
                                                            'area': area,
                                                            'province': province,
                                                            'ccaa': ccaa,
                                                            })

        return render(request, self.template_name, {'form': form})


class NixnoxPyFormView(View):

    template_name = 'forms/obs_form.html'
    form_class = NixnoxPyForm
    success_url = ''

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            values_view = request.FILES.values()
            value_iterator = iter(values_view)
            TAS_file = next(value_iterator)

            if TAS_file.size > 15000:
                return render(request, self.template_name, {'not_valid': True})

            else:

                TAS_instance = form.save()

                path = TAS_instance.measurements_file.path

                meta_dict = {
                    'author': TAS_instance.author.username,
                    'Datetime': TAS_instance.date,
                    'institution': TAS_instance.institution.name,
                    'photometer': TAS_instance.photometer.serial_id,
                    'place': TAS_instance.place,
                    'comments': TAS_instance.comments,
                }

                new_map = NixnoxPy(path, meta_dict, name = TAS_instance.place)
                map_path, ecsv_path, data, mag, azi, alt, lat, long = new_map.pipeline()

                # Looks for the place
                location = geolocator.reverse(
                    f"{lat.to_string(decimal = True)}, {long.to_string(decimal = True)}",
                    exactly_one = True, zoom = 10)
                address = location.address.split(', ')

                area, province, ccaa = (address[0], address[1], address[2])

                ecsv_filename = ecsv_path.split('/')[-1]
                map_filename = map_path.split('/')[-1]

                TAS_instance.location = area
                TAS_instance.region = province
                TAS_instance.state = ccaa

                TAS_instance.gispoint = Point(np.mean(data['Long']), np.mean(data['Lat']))

                TAS_instance.date = data['Datetime'][0].datetime
                TAS_instance.save()

                obs_analysis.delay(f'{TAS_instance.id}')
                pandas_sql_py.delay(data, TAS_instance, alt, azi, mag)

                return render(request, self.template_name, {
                    'map_path': map_path.split('nixnox_project')[1],
                    'ecsv_path': ecsv_path.split('nixnox_project')[1],
                    'ecsv_filename': ecsv_filename,
                    'map_filename': map_filename,
                    'user': TAS_instance.author,
                    'lat': np.mean(data['Lat']),
                    'long': np.mean(data['Long']),
                    'area': area,
                    'province': province,
                    'ccaa': ccaa,
                })

        return render(request, self.template_name, {'form': form})


class QueryView(ListView):
    paginate_by = 10
    model = Observation
    template_name = 'query/query.html'


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class QueryMapView(View):
    template_name = 'query/map_query.html'
    form_class = QueryPointForm

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():
            instance = form.clean()
            pnt = instance['query_point']
            distance = instance['distance']
            queryset = Observation.objects.filter(gispoint__distance_lte=(pnt, D(km=distance)))

            # Measurements queryset
            qs = Measurement.objects.filter(
                interpolated=False,
                observation__id__in = queryset
            )
            query_path = f'media/tmp/{id_generator()}.csv'
            with open(query_path,'wb') as csv_file:
                write_csv(qs, csv_file)

            return render(request, self.template_name, {
                'query': queryset,
                'instance': instance,
                'query_path': '/' + query_path
            })

        return render(request, self.template_name, {'form': form})