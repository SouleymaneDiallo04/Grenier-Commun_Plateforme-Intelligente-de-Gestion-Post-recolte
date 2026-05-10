from django.urls import path
from . import views
app_name = 'warrantage'
urlpatterns = [
    path('demande/<int:pk>/', views.detail_demande, name='detail_demande'),
]
