import pandas as pd
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, RecipeIngredient
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data_path = Path(settings.BASE_DIR) / 'data' / 'ingredients.csv'
        try:
            df = pd.read_csv(data_path, encoding='utf-8', header=None)

            ingredients_to_create = []
            for index, row in df.iterrows():
                ingredient_name = row[0]
                measurement_unit = row[1]

                if ingredient_name:
                    amount = 1
                    ingredients_to_create.append(
                        RecipeIngredient(
                            ingredient=Ingredient.objects.get_or_create(
                                name=ingredient_name,
                                measurement_unit=measurement_unit
                            )[0],
                            amount=amount
                        )
                    )

            RecipeIngredient.objects.bulk_create(ingredients_to_create,
                                                 ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно добавлены'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV файл не найден.'))
