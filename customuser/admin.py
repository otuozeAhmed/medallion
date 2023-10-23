from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'unit', 'staff_id',)
    search_fields = ('department', 'unit',)
    list_filter = ('department', 'unit',)

admin.site.register(CustomUser, CustomUserAdmin)