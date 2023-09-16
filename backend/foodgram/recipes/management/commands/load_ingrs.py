import pandas as pd
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        data_path = Path(settings.BASE_DIR) / 'data' / 'ingredients.csv'

        try:
            # Установим header=None, так как у нас нет заголовков в CSV файле
            df = pd.read_csv(data_path, encoding='utf-8', header=None)

            for index, row in df.iterrows():
                # Первый столбец содержит имя ингредиента
                ingredient_name = row[0]
                # Второй столбец содержит единицу измерения (если есть)
                measurement_unit = row[1]

                if ingredient_name:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=ingredient_name,
                        measurement_unit=measurement_unit
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f'Создан ингредиент: {ingredient}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f'Ингредиент уже существует: {ingredient}'))

            self.stdout.write(self.style.SUCCESS(
                'С ингредиентами всё в порядке'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                'CSV файл не найден.'))
