import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, **options):
        with open("data/tags.csv", encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            Tag.objects.bulk_create([
                Tag(
                    name=line[0],
                    color=line[1],
                    slug=line[2]
                ) for num, line in enumerate(reader)
            ])
