import csv
import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

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
                Ingredient.objects.bulk_create(
                    Ingredient(**data) for data in reader)
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно загруженны!'))
        except FileNotFoundError:
            raise CommandError('Файл отсутствует в директории data')
