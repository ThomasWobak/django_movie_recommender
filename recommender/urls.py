from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='search'),
    path('results/', views.search_results_view, name='search_results'),
    path('recommendations/<int:movie_id>/', views.recommendations_view, name='recommendations'),
]