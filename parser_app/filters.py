from django_filters import rest_framework as filters
from .models import Vacancy


class VacancyFilter(filters.FilterSet):
    """Фильтры для вакансий"""
    min_salary = filters.NumberFilter(field_name='salary_from', lookup_expr='gte')
    max_salary = filters.NumberFilter(field_name='salary_to', lookup_expr='lte')
    company = filters.CharFilter(field_name='company', lookup_expr='icontains')
    has_salary = filters.BooleanFilter(method='filter_has_salary')
    skills = filters.CharFilter(method='filter_skills')
    date_from = filters.DateFilter(field_name='published_at', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='published_at', lookup_expr='lte')
    
    class Meta:
        model = Vacancy
        fields = {
            'name': ['icontains'],
            'area': ['exact', 'icontains'],
            'experience': ['exact'],
            'employment': ['exact'],
            'parse_task': ['exact'],
        }
    
    def filter_has_salary(self, queryset, name, value):
        """Фильтр по наличию зарплаты"""
        if value:
            return queryset.filter(salary_from__isnull=False) | queryset.filter(salary_to__isnull=False)
        return queryset.filter(salary_from__isnull=True, salary_to__isnull=True)
    
    def filter_skills(self, queryset, name, value):
        """Фильтр по навыкам"""
        skills = [skill.strip() for skill in value.split(',') if skill.strip()]
        if skills:
            from django.db.models import Q
            query = Q()
            for skill in skills:
                query |= Q(skills__contains=[skill])
            return queryset.filter(query)
        return queryset