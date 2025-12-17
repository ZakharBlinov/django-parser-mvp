from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import rest_framework as filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Vacancy, ParseTask
from .serializers import VacancySerializer, ParseTaskSerializer
from .filters import VacancyFilter
from .services.parser import JobParser


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all().order_by('-published_at')
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = VacancyFilter
    
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        vacancies = self.get_queryset()[:limit]
        serializer = self.get_serializer(vacancies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = {
            'total': Vacancy.objects.count(),
            'with_salary': Vacancy.objects.exclude(
                salary_from__isnull=True, salary_to__isnull=True
            ).count(),
            'companies': Vacancy.objects.values('company').distinct().count(),
            'areas': Vacancy.objects.values('area').distinct().count(),
        }
        return Response(stats)


class ParseTaskViewSet(viewsets.ModelViewSet):
    queryset = ParseTask.objects.all()
    serializer_class = ParseTaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        task = self.get_object()
        parser = JobParser()
        stats = parser.parse_task(task)
        
        return Response({
            'status': 'success',
            'task': task.name,
            'stats': stats
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        tasks = ParseTask.objects.filter(is_active=True)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class VacancyListView(ListView):
    model = Vacancy
    template_name = 'vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10
    
    def get_queryset(self):
        return Vacancy.objects.all().order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_count'] = Vacancy.objects.count()
        context['with_salary_count'] = Vacancy.objects.exclude(
            salary_from__isnull=True, salary_to__isnull=True
        ).count()
        context['companies_count'] = Vacancy.objects.values('company').distinct().count()
        context['areas_count'] = Vacancy.objects.values('area').distinct().count()
        
        return context


class VacancyDetailView(DetailView):
    model = Vacancy
    template_name = 'vacancy_detail.html'
    context_object_name = 'vacancy'