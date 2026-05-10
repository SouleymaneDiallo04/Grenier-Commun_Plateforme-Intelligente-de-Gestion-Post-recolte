from django.urls import path
from . import views
app_name = 'imf'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dossiers/', views.dossiers, name='dossiers'),
    path('dossier/<int:pk>/', views.detail_dossier, name='detail_dossier'),
    path('dossier/<int:pk>/decider/', views.decider_dossier, name='decider_dossier'),
]
