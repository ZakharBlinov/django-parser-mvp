from django.contrib import admin
from .models import ParseTask, Vacancy


@admin.register(ParseTask)
class ParseTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'search_query', 'area', 'pages', 'is_active', 'created_at', 'last_run')
    list_filter = ('source', 'is_active', 'created_at')
    search_fields = ('name', 'search_query')
    list_editable = ('is_active', 'pages')
    readonly_fields = ('created_at', 'last_run')
    
    fieldsets = (
        ('Основные настройки', {
            'fields': ('name', 'source', 'is_active')
        }),
        ('Параметры поиска', {
            'fields': ('search_query', 'area', 'per_page', 'pages')
        }),
        ('Даты', {
            'fields': ('created_at', 'last_run'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'salary_display', 'area', 'published_at')
    list_filter = ('parse_task', 'area', 'salary_currency', 'published_at')
    search_fields = ('name', 'company', 'description', 'skills')
    readonly_fields = ('external_id', 'created_at')
    list_per_page = 20
    
    def salary_display(self, obj):
        return obj.salary or "Не указана"
    salary_display.short_description = 'Зарплата'