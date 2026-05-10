from django.urls import path
from . import views
app_name = 'silos'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('depot/nouveau/', views.nouveau_depot, name='nouveau_depot'),
    path('depot/<int:pk>/', views.detail_depot, name='detail_depot'),
    path('retrait/<int:depot_pk>/', views.enregistrer_retrait, name='enregistrer_retrait'),
    path('alertes/', views.alertes, name='alertes'),
    path('alertes/<int:pk>/acquitter/', views.acquitter_alerte, name='acquitter_alerte'),
    path('rapport/', views.rapport_mensuel, name='rapport_mensuel'),
    path('conditions/mettre-a-jour/', views.mettre_a_jour_conditions, name='maj_conditions'),
]
