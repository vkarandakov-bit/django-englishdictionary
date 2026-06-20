from django.core.management.base import BaseCommand

from dictionary.services import seed_common_words


class Command(BaseCommand):
    help = 'Заполняет базу общим набором английских слов'

    def handle(self, *args, **options):
        seed_common_words()
        self.stdout.write(self.style.SUCCESS('Базовые слова добавлены.'))
