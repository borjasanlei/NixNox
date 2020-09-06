from django.contrib.gis import forms
from .models import Observation

from leaflet.forms.widgets import LeafletWidget


class TASObservationForm(forms.ModelForm):

    class Meta:
        model = Observation
        fields = ('author',
				  'institution',
				  'photometer',
				  'place',
				  'humidity',
				  'comments',
				  'measurements_file',)

class NixnoxPyForm(forms.ModelForm):
	# gispoint = forms.PointField(widget=forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}))

	class Meta:
		model = Observation
		fields = ('author',
				  'date',
				  'institution',
				  'photometer',
				  'place',
				  #'gispoint',
				  'humidity',
				  'comments',
				  'measurements_file',
				  )

class QueryPointForm(forms.Form):
	query_point = forms.PointField(widget=
        forms.OSMWidget(attrs={'map_width': 700,
							   'map_height': 500,
							   'default_lat': 40.304665,
							   'default_lon': -3.723679,
							   'default_zoom': 6
		}))
	distance = forms.DecimalField(max_digits = 6, decimal_places = 2, help_text = 'Distance in km.')
