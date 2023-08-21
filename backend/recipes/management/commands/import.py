import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт из файла'

    def handle(self, *args, **options):
        print('Поехали!')
        with open(
            'recipes/data/ingredients.csv', encoding='utf-8'
        ) as data_csv:
            for row in csv.DictReader(data_csv, delimiter=','):
                try:
                    Ingredient.objects.get_or_create(**row)
                except Exception as error:
                    print(f'Все фигня, давай по новой {error}')
        print('Усё приехали.')
