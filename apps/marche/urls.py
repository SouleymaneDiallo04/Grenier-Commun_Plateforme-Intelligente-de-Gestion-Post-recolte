from django.urls import path
from . import views
app_name = 'marche'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('offre/nouvelle/', views.nouvelle_offre, name='nouvelle_offre'),
    path('offre/<int:pk>/', views.detail_offre, name='detail_offre'),
    path('transactions/', views.mes_transactions, name='mes_transactions'),
]
