from django.conf import settings 
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Dajngo admin
    path('admin/', admin.site.urls),

    # User management
    #path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    

    # Local apps
    #path('accounts/', include('users.urls')),
	path('', include('pages.urls')),
	path('allskymaps/', include('allskymaps.urls'), name='allskymaps'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
