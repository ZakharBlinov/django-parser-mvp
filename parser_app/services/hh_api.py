import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class HHAPIClient:
    """Клиент для работы с API HeadHunter"""
    
    BASE_URL = "https://api.hh.ru"
    
    def __init__(self, user_agent: str = "JobParser/1.0 (admin@example.com)"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json',
        })
    
    def search_vacancies(
        self,
        text: str = "python",
        area: str = "1",
        per_page: int = 50,
        page: int = 0,
        only_with_salary: bool = False
    ) -> Optional[Dict]:
        """
        Поиск вакансий через API HH
        
        Args:
            text: Поисковый запрос
            area: ID региона
            per_page: Количество вакансий на странице
            page: Номер страницы
            only_with_salary: Только вакансии с зарплатой
        
        Returns:
            Словарь с результатами поиска
        """
        params = {
            'text': text,
            'area': area,
            'per_page': per_page,
            'page': page,
            'only_with_salary': only_with_salary,
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/vacancies",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API HH: {e}")
            return None
    
    def get_vacancy_details(self, vacancy_id: str) -> Optional[Dict]:
        """
        Получение детальной информации о вакансии
        
        Args:
            vacancy_id: ID вакансии
        
        Returns:
            Словарь с детальной информацией о вакансии
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/vacancies/{vacancy_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении деталей вакансии {vacancy_id}: {e}")
            return None
    
    @staticmethod
    def parse_vacancy_data(vacancy_data: Dict) -> Dict:
        """
        Парсинг данных вакансии из ответа API
        
        Args:
            vacancy_data: Словарь с данными вакансии из API
        
        Returns:
            Словарь с обработанными данными
        """
        salary_data = vacancy_data.get('salary')
        salary_from = salary_to = salary_currency = salary_gross = None
        
        if salary_data:
            salary_from = salary_data.get('from')
            salary_to = salary_data.get('to')
            salary_currency = salary_data.get('currency')
            salary_gross = salary_data.get('gross')
        
        published_at_str = vacancy_data.get('published_at')
        published_at = None
        if published_at_str:
            try:
                published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                published_at = timezone.make_aware(published_at)
            except (ValueError, TypeError):
                published_at = timezone.now()
        
        skills = []
        if vacancy_data.get('key_skills'):
            skills = [skill['name'] for skill in vacancy_data['key_skills']]
        
        return {
            'external_id': vacancy_data.get('id'),
            'name': vacancy_data.get('name'),
            'company': vacancy_data.get('employer', {}).get('name', 'Не указано'),
            'salary_from': salary_from,
            'salary_to': salary_to,
            'salary_currency': salary_currency,
            'salary_gross': salary_gross,
            'experience': vacancy_data.get('experience', {}).get('name'),
            'schedule': vacancy_data.get('schedule', {}).get('name'),
            'employment': vacancy_data.get('employment', {}).get('name'),
            'description': vacancy_data.get('description'),
            'skills': skills,
            'area': vacancy_data.get('area', {}).get('name', 'Не указано'),
            'url': vacancy_data.get('alternate_url'),
            'published_at': published_at,
        }