from django.urls import path
from . import views
app_name = 'administration'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('silos/', views.gestion_silos, name='gestion_silos'),
    path('utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('warrantage/', views.gestion_warrantage, name='gestion_warrantage'),
    path('marche/', views.gestion_marche, name='gestion_marche'),
    path('finances/', views.finances, name='finances'),
    path('donnees/', views.donnees, name='donnees'),
    path('traductions/', views.traductions, name='traductions'),
]
