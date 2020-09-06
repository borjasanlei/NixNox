from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Photometer, Institution

from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username']

admin.site.register(CustomUser, CustomUserAdmin)

class PhotometerAdmin(admin.ModelAdmin):
    list_display = ('serial_id', 'user')
    list_filter = ('user',)
    
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name','id')
    
admin.site.register(Photometer, PhotometerAdmin)
admin.site.register(Institution, InstitutionAdmin)
