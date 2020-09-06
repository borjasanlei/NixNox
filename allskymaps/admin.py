from django.contrib import admin
from .models import Observation, Measurement, KocijafBara
from django.contrib.gis.admin import OSMGeoAdmin


class ObservationAdmin(OSMGeoAdmin):

	list_display = ('author', 'location', 'photometer', 'publish', 'id')

	fields = (
		('author', 'photometer'),
		('date', 'publish'),
		('gispoint'),
		'place',
		('location', 'region', 'state'),
		('temperature', 'humidity'), 
		#'image',
		'comments', 
		'measurements_file',
		)

	list_filter = ('author',)


class MeasurementAdmin(admin.ModelAdmin):
	list_display = (
		'observation',
		'azimuth',
		'elevation',
		'mag_value',
	'observation_id')

	list_filter = ('observation__id',)
	pass

class KocijafBaraAdmin(admin.ModelAdmin):
	pass

admin.site.register(Observation, ObservationAdmin)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(KocijafBara, KocijafBaraAdmin)
