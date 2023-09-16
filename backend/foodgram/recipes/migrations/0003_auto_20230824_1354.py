# Generated by Django 3.0.5 on 2023-08-24 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230824_1232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='tag',
        ),
        migrations.AddField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(related_name='recipes_tag', to='recipes.Tag'),
        ),
    ]
