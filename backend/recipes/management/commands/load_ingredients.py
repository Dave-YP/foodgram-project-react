import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, **options):
        with open("data/ingredients.csv", encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            Ingredient.objects.bulk_create([
                Ingredient(
                    name=line[0],
                    measurement_unit=line[1]
                ) for num, line in enumerate(reader)
            ])
