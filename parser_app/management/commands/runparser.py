from django.core.management.base import BaseCommand
from django.utils import timezone
import logging
from parser_app.services.parser import JobParser
from parser_app.models import ParseTask

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запуск парсинга вакансий'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--task-id',
            type=int,
            help='ID конкретной задачи для парсинга'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Запустить все активные задачи'
        )
    
    def handle(self, *args, **options):
        parser = JobParser()
        
        if options['task_id']:
            self.stdout.write(f"Запуск парсинга задачи ID: {options['task_id']}")
            stats = parser.parse_by_id(options['task_id'])
            self._print_stats(stats)
        
        elif options['all']:
            tasks = ParseTask.objects.filter(is_active=True)
            self.stdout.write(f"Найдено активных задач: {tasks.count()}")
            
            for task in tasks:
                self.stdout.write(f"\nОбработка задачи: {task.name} (ID: {task.id})")
                stats = parser.parse_task(task)
                self._print_stats(stats)
        
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Укажите параметры: --task-id ID или --all для запуска всех задач\n"
                    "Пример: python manage.py runparser --all"
                )
            )
    
    def _print_stats(self, stats):
        """Вывод статистики в консоль"""
        if 'error' in stats:
            self.stdout.write(self.style.ERROR(f"Ошибка: {stats['error']}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Статистика: найдено {stats.get('total_found', 0)}, "
                f"обработано {stats.get('parsed', 0)}, "
                f"добавлено {stats.get('added', 0)}, "
                f"обновлено {stats.get('updated', 0)}, "
                f"ошибок {stats.get('errors', 0)}, "
                f"страниц {stats.get('pages_processed', 0)}"
            ))