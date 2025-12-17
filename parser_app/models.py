from django.db import models
from django.utils import timezone


class ParseTask(models.Model):
    """Модель для хранения конфигураций парсинга"""
    SOURCE_CHOICES = [
        ('hh', 'HeadHunter'),
        ('habr', 'Habr Career'),
    ]
    
    name = models.CharField('Название задачи', max_length=255)
    source = models.CharField('Источник', max_length=50, choices=SOURCE_CHOICES, default='hh')
    search_query = models.CharField('Поисковый запрос', max_length=255, default='python')
    area = models.CharField('Регион', max_length=100, default='1')
    per_page = models.IntegerField('Кол-во вакансий на странице', default=50)
    pages = models.IntegerField('Кол-во страниц', default=1)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    last_run = models.DateTimeField('Последний запуск', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Задача парсинга'
        verbose_name_plural = 'Задачи парсинга'
    
    def __str__(self):
        return f"{self.name} ({self.get_source_display()})"


class Vacancy(models.Model):
    """Модель для хранения вакансий"""
    CURRENCY_CHOICES = [
        ('RUR', 'Рубли'),
        ('USD', 'Доллары'),
        ('EUR', 'Евро'),
    ]
    
    parse_task = models.ForeignKey(ParseTask, on_delete=models.CASCADE, related_name='vacancies', verbose_name='Задача парсинга')
    external_id = models.CharField('ID вакансии', max_length=50, unique=True)
    name = models.CharField('Название вакансии', max_length=500)
    company = models.CharField('Компания', max_length=500)
    salary_from = models.IntegerField('Зарплата от', null=True, blank=True)
    salary_to = models.IntegerField('Зарплата до', null=True, blank=True)
    salary_currency = models.CharField('Валюта', max_length=10, choices=CURRENCY_CHOICES, null=True, blank=True)
    salary_gross = models.BooleanField('Зарплата до вычета налогов', null=True)
    experience = models.CharField('Опыт работы', max_length=100, null=True, blank=True)
    schedule = models.CharField('График работы', max_length=100, null=True, blank=True)
    employment = models.CharField('Тип занятости', max_length=100, null=True, blank=True)
    description = models.TextField('Описание вакансии', null=True, blank=True)
    skills = models.JSONField('Навыки', default=list)
    area = models.CharField('Регион', max_length=200)
    url = models.URLField('Ссылка на вакансию', max_length=500)
    published_at = models.DateTimeField('Дата публикации')
    created_at = models.DateTimeField('Дата создания записи', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-published_at']
    
    def __str__(self):
        return self.name
    
    @property
    def salary(self):
        """Форматированное представление зарплаты"""
        if not self.salary_from and not self.salary_to:
            return None
        
        salary_parts = []
        if self.salary_from:
            salary_parts.append(f"от {self.salary_from:,}".replace(',', ' '))
        if self.salary_to:
            salary_parts.append(f"до {self.salary_to:,}".replace(',', ' '))
        
        result = ' '.join(salary_parts)
        if self.salary_currency:
            currency_symbol = {'RUR': '₽', 'USD': '$', 'EUR': '€'}.get(self.salary_currency, self.salary_currency)
            result += f' {currency_symbol}'
            if self.salary_gross is not None:
                result += ' (до вычета налогов)' if self.salary_gross else ' (на руки)'
        
        return result