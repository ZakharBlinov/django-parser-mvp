import time
from typing import List, Optional
from django.utils import timezone
from django.db import transaction
import logging

from .hh_api import HHAPIClient
from parser_app.models import ParseTask, Vacancy

logger = logging.getLogger(__name__)


class JobParser:
    """Основной класс парсера вакансий"""
    
    def __init__(self):
        self.api_client = HHAPIClient()
    
    def parse_task(self, task: ParseTask) -> dict:
        """
        Выполнение задачи парсинга
        
        Args:
            task: Объект задачи парсинга
        
        Returns:
            Словарь со статистикой выполнения
        """
        stats = {
            'total_found': 0,
            'parsed': 0,
            'added': 0,
            'updated': 0,
            'errors': 0,
            'pages_processed': 0,
        }
        
        logger.info(f"Начало парсинга задачи: {task.name}")
        
        try:
            for page in range(task.pages):
                logger.info(f"Обработка страницы {page + 1}/{task.pages}")
                
                result = self.api_client.search_vacancies(
                    text=task.search_query,
                    area=task.area,
                    per_page=task.per_page,
                    page=page
                )
                
                if not result:
                    logger.warning(f"Не удалось получить данные для страницы {page}")
                    stats['errors'] += 1
                    continue
                
                stats['total_found'] = result.get('found', 0)
                vacancies_data = result.get('items', [])
                
                for vacancy_data in vacancies_data:
                    try:
                        processed = self._process_vacancy(vacancy_data, task)
                        if processed == 'added':
                            stats['added'] += 1
                        elif processed == 'updated':
                            stats['updated'] += 1
                        stats['parsed'] += 1
                    except Exception as e:
                        logger.error(f"Ошибка при обработке вакансии {vacancy_data.get('id')}: {e}")
                        stats['errors'] += 1
                
                stats['pages_processed'] += 1
                
                if page < task.pages - 1:
                    time.sleep(0.5)
            
            task.last_run = timezone.now()
            task.save(update_fields=['last_run'])
            
            logger.info(f"Парсинг завершен. Статистика: {stats}")
            
        except Exception as e:
            logger.error(f"Критическая ошибка при парсинге задачи {task.id}: {e}")
            stats['errors'] += 1
        
        return stats
    
    def _process_vacancy(self, vacancy_data: dict, task: ParseTask) -> Optional[str]:
        """
        Обработка и сохранение одной вакансии
        
        Args:
            vacancy_data: Данные вакансии из API
            task: Задача парсинга
        
        Returns:
            'added' - если вакансия добавлена,
            'updated' - если вакансия обновлена,
            None - если произошла ошибка
        """
        external_id = vacancy_data.get('id')
        if not external_id:
            logger.warning("Вакансия без ID, пропускаем")
            return None
        
        if not vacancy_data.get('salary') or not vacancy_data.get('description'):
            detailed_data = self.api_client.get_vacancy_details(external_id)
            if detailed_data:
                vacancy_data.update(detailed_data)
        
        parsed_data = self.api_client.parse_vacancy_data(vacancy_data)
        if not parsed_data['external_id']:
            logger.warning(f"Не удалось распарсить данные вакансии: {external_id}")
            return None
        
        with transaction.atomic():
            existing_vacancy = Vacancy.objects.filter(external_id=parsed_data['external_id']).first()
            
            if existing_vacancy:
                for field, value in parsed_data.items():
                    if field != 'external_id':
                        setattr(existing_vacancy, field, value)
                existing_vacancy.parse_task = task
                existing_vacancy.save()
                return 'updated'
            else:
                Vacancy.objects.create(parse_task=task, **parsed_data)
                return 'added'
    
    def parse_by_id(self, task_id: int) -> dict:
        """
        Запуск парсинга по ID задачи
        
        Args:
            task_id: ID задачи парсинга
        
        Returns:
            Статистика выполнения
        """
        try:
            task = ParseTask.objects.get(id=task_id, is_active=True)
            return self.parse_task(task)
        except ParseTask.DoesNotExist:
            logger.error(f"Задача парсинга {task_id} не найдена или неактивна")
            return {'error': 'Task not found or inactive'}