from rest_framework import serializers
from .models import Vacancy, ParseTask


class VacancySerializer(serializers.ModelSerializer):
    """Сериализатор для вакансий"""
    salary_display = serializers.SerializerMethodField()
    parse_task_name = serializers.CharField(source='parse_task.name', read_only=True)
    
    class Meta:
        model = Vacancy
        fields = [
            'id', 'external_id', 'name', 'company', 'salary_from', 'salary_to',
            'salary_currency', 'salary_display', 'experience', 'schedule',
            'employment', 'description', 'skills', 'area', 'url', 'published_at',
            'created_at', 'parse_task', 'parse_task_name'
        ]
        read_only_fields = ['created_at']
    
    def get_salary_display(self, obj):
        return obj.salary


class ParseTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач парсинга"""
    vacancies_count = serializers.SerializerMethodField()
    last_run_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ParseTask
        fields = [
            'id', 'name', 'source', 'search_query', 'area', 'per_page', 'pages',
            'is_active', 'created_at', 'last_run', 'last_run_formatted', 'vacancies_count'
        ]
        read_only_fields = ['created_at', 'last_run']
    
    def get_vacancies_count(self, obj):
        return obj.vacancies.count()
    
    def get_last_run_formatted(self, obj):
        if obj.last_run:
            return obj.last_run.strftime('%d.%m.%Y %H:%M')
        return None