from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vacancies', views.VacancyViewSet, basename='vacancy')
router.register(r'tasks', views.ParseTaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('vacancies/latest/', views.VacancyViewSet.as_view({'get': 'latest'}), name='vacancies-latest'),
    path('vacancies/stats/', views.VacancyViewSet.as_view({'get': 'stats'}), name='vacancies-stats'),
]
