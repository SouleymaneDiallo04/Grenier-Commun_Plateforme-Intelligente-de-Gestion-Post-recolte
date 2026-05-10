from django.urls import path
from . import views
app_name = 'traduction'
urlpatterns = [
    path('', views.traduire, name='traduire'),
    path('historique/', views.historique, name='historique'),
    path('evaluer/<int:pk>/', views.evaluer, name='evaluer'),
    path('api/traduire/', views.api_traduire, name='api_traduire'),
]
