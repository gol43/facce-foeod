# Generated by Django 3.2.20 on 2023-09-13 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20230911_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipetag',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='recipetag',
            name='tag',
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={},
        ),
        migrations.AlterModelOptions(
            name='subscribe',
            options={},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_shopping_cart',
        ),
        migrations.RemoveConstraint(
            model_name='subscribe',
            name='unique_subscription',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='tags',
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='tag', to='recipes.tag'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
        migrations.DeleteModel(
            name='RecipeTag',
        ),
    ]
