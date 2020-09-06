from django.urls import path
from .views import TASFormView, NixnoxPyFormView, QueryView, QueryMapView

urlpatterns = [
	path('TAS-form/', TASFormView.as_view(), name='TAS_form'),
	path('Nixnox-form/py/', NixnoxPyFormView.as_view(), name='Nixnox_py_form'),
	path('query/', QueryView.as_view(), name='query-page'),
	path('query-map/', QueryMapView.as_view(), name='query-map-page'),
]
