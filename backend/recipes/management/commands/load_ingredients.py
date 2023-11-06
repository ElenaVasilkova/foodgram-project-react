import csv
import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из файла ingredients.csv'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(DATA_ROOT, options['filename']),
                'r',
                encoding='utf-8'
            ) as file:
                reader = csv.DictReader(file)
                for data in reader:
                    name, measurement_unit = data
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно загруженны!'))
        except FileNotFoundError:
            raise CommandError(
                'Добавьте файл ingredients.csv в директорию /data'
            )
