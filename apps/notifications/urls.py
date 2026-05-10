from django.urls import path
from . import views
app_name = 'notifications'
urlpatterns = [
    path('', views.liste, name='liste'),
    path('<int:pk>/lire/', views.marquer_lu, name='marquer_lu'),
]
