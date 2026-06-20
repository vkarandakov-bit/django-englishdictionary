from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('study/', views.study, name='study'),
    path('add/', views.add_word, name='add_word'),
    path('delete/', views.delete_word_view, name='delete_word'),
    path('stats/', views.statistics, name='statistics'),
    path('schema/', views.schema, name='schema'),
]
