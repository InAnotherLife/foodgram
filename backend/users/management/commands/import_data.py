from csv import reader

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в БД.'

    def handle(self, *args, **options):
        try:
            with open('data/ingredients.csv', 'r', encoding='utf8') as file:
                file_reader = reader(file)
                for row in file_reader:
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
            with open('data/tags.csv', 'r', encoding='utf8') as file:
                file_reader = reader(file)
                for row in file_reader:
                    Tag.objects.get_or_create(
                        name=row[0],
                        color=row[1],
                        slug=row[2]
                    )
            self.stdout.write(self.style.SUCCESS(
                'Данные успешно загружены в БД.')
            )
        except Exception as error:
            raise Exception('Ошибка при импорте данных:', error)
