from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Создаем тэги'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#b3ffa3', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#ffbfa3', 'slug': 'dinner'},
            {'name': 'Ужин', 'color': '##a6a3ff', 'slug': 'supper'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Тэги успешно загруженны!'))
