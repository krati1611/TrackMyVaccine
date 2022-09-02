from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path('forgot/', views.forgot),
    path('register/', views.register),
    path('dashboard/', views.dashboard),
    path('logout/', views.logout),
    path('changepassword/', views.changepassword),
    path('edit/', views.edit),
    path('appointment/', views.appointment),
    path('appointment/cancel/<int:a_id>/', views.cancel_appointment),
    path('book/', views.book),
    path('book1/', views.book1),
    path('book/<int:h_id>/<int:v_id>/<int:d_id>/<str:date>/<int:s_id>', views.confirmbook),
    path('verify/<str:email>/', views.verifyemail),

]
