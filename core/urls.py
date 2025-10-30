# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('signup-success/', views.success_view, name='success_page'),
    path('upload-resume/', views.resume_upload_view, name='resume_upload'),
    path('results/', views.results_view, name='results_page'), 
]