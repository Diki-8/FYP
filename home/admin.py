from django.contrib import admin
from home.models import Contact, Dog, TimeSlot, Booking

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date')
    search_fields = ('name', 'email')

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'owner')
    list_filter = ('breed',)
    search_fields = ('name', 'owner__username')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('get_service_type_display', 'start_time', 'end_time')
    list_filter = ('service_type',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('dog', 'get_service_display', 'date', 'time_slot', 'user')
    list_filter = ('service', 'date')
    search_fields = ('dog__name', 'user__username')