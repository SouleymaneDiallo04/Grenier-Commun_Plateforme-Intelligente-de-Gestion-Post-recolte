from django.urls import path
from . import views
app_name = 'agriculteurs'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('stock/', views.mes_stocks, name='mes_stocks'),
    path('depot/<int:pk>/', views.detail_depot, name='detail_depot'),
    path('prix/', views.prix_marche, name='prix_marche'),
    path('warrantage/', views.mes_warrantages, name='mes_warrantages'),
    path('warrantage/demander/<int:depot_pk>/', views.demander_warrantage, name='demander_warrantage'),
    path('ventes/', views.mes_ventes, name='mes_ventes'),
    path('profil/', views.mon_profil, name='mon_profil'),
]
