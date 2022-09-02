from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path('forgot/', views.forgot),
    path('register/', views.register),
    path('dashboard/', views.dashboard),
    path('logout/', views.logout),
    path('changepassword/', views.changepassword),
    path('stock/', views.stock),
    path('expiryremove/<int:e_id>/', views.expiryremove),
    path('addvaccine/', views.addvaccine),
    path('edit/', views.edit),
    path('appointment/', views.appointment),
    path('appointment/<str:key>/', views.appointment),
    path('appointment/verifyaadhar/<int:a_id>/', views.verifyaadhar),
    path('slot/', views.slot),
    path('verify/<str:email>/', views.verifyemail),
]
