from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Province, City, Address

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("اطلاعات تکمیلی", {
            'fields': ('phone', 'profile_image', 'address'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("اطلاعات تکمیلی", {
            'fields': ('phone', 'profile_image', 'address'),
        }),
    )
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'province')
    search_fields = ('name',)
    list_filter = ('province',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'province', 'city', 'receiver_name', 'receiver_phone', 'postal_code', 'is_default')
    search_fields = ('user__email', 'receiver_name', 'receiver_phone', 'postal_code')
    list_filter = ('province', 'city', 'is_default')
