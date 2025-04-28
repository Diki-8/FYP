from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
   path("", views.index, name='home'),
   path("about/", views.about, name='about'),
   path("services/", views.services, name='services'),
   path("services/daycare/", views.daycare, name='services'),
   path("services/petgrooming/", views.petgrooming, name='services'),
   path("services/boarding/", views.boarding, name='services'),
   path("contact/", views.contact, name='contact'),
   path("signin/", views.signin, name='signin'),
   path("signup/", views.signup, name='signup'),
   path('logout/', views.user_logout, name='logout'),
   path('services/boarding/', views.boarding, name='boarding'),
   path('services/daycare/', views.daycare, name='daycare'),
   path('services/petgrooming/', views.petgrooming, name='petgrooming'),
   path("edit_profile/", views.edit_profile, name="edit_profile"),
   path('userprofile/', views.userprofile, name='userprofile'),
   path('mybookings/', views.mybookings, name='mybookings'),
   path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
   path('adminpanel/', views.admin_dashboard, name='adminpanel'),
   path('adminpanel/booking/<int:booking_id>/cancel/', views.admin_cancel_booking, name='admin_cancel_booking'),
   path('adminpanel/booking/<int:booking_id>/complete/', views.admin_complete_booking, name='admin_complete_booking'),
   path('adminpanel/undo-cancel-booking/<int:booking_id>/', views.admin_undo_cancel_booking, name='admin_undo_cancel_booking'),
   path('adminpanel/contacts/', views.contact_admin_view, name='contact_admin'),
   path("booking/grooming/", views.booking_grooming, name="booking_grooming"),
   path("booking/daycare/", views.booking_daycare, name="booking_daycare"),
   path("booking/boarding/", views.booking_boarding, name="booking_boarding"),
   path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),

   
]