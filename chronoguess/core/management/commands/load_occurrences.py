from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from chronoguess.core.models import Occurrence

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        print("Loading occurrences from CSV...")
        with open(f"{settings.BASE_DIR}/occurrences.csv", 'r') as file:
            for line in file.readlines()[1:]:
                parts = line.strip().split(',')
                if len(parts) != 4:
                    continue
                title, summary, photo_url, year = parts
                Occurrence.objects.get_or_create(
                    title=title,
                    summary=summary,
                    photo_url=photo_url,
                    year=int(year)
                )