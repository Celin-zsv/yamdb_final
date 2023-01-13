import csv
import os

from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import Category, Genre, Review, Title, User, Comment


class Command(BaseCommand):
    help = 'Import data from /static/data'

    def handle(self, *args, **options):
        def model_import(csv_name, model_class, model_fields):
            path = os.path.join(BASE_DIR, 'static/data', csv_name)
            with open(path, encoding='utf-8') as r_file:
                reader = csv.reader(r_file, delimiter=",")
                next(reader)
                upload_list = []
                for row in reader:
                    # по-хорошему, кроме проверки на наличие ID,
                    # надо верифицировать поля, но пока так
                    if not model_class.objects.filter(
                            pk=row[model_fields.index('id')]).exists():
                        item = model_class()
                        for row_number, field_name in enumerate(model_fields):
                            setattr(item, field_name, row[row_number])
                        upload_list.append(item)
                model_class.objects.bulk_create(upload_list)
                print(f'Загружено {len(upload_list)} '
                      f'записей в {model_class.__name__}.')

        models_and_csv = [
            ('users.csv',
             User,
             ('id', 'username', 'email', 'role',
              'bio', 'first_name', 'last_name',)
             ),
            ('category.csv',
             Category,
             ('id', 'name', 'slug')
             ),
            ('genre.csv',
             Genre,
             ('id', 'name', 'slug')
             ),
            ('titles.csv',
             Title,
             ('id', 'name', 'year', 'category_id')
             ),
            ('review.csv',
             Review,
             ('id', 'title_id', 'text', 'author_id', 'score', 'pub_date')
             ),
            ('comments.csv',
             Comment,
             ('id', 'review_id', 'text', 'author_id', 'pub_date')
             ),
        ]

        for model in models_and_csv:
            model_import(*model)

        # Загружаем жанротайтлы
        path = os.path.join(BASE_DIR, 'static/data', 'genre_title.csv')
        with open(path, encoding='utf-8') as r_file:
            reader = csv.reader(r_file, delimiter=",")
            next(reader)
            items_counter = 0
            for row in reader:
                if not Title.objects.filter(
                        pk=row[1], genre__id=row[2]).exists():
                    Title.objects.get(pk=row[1]).genre.add(row[2])
                    items_counter += 1
            print(f'Загружено {items_counter} записей в жанротайтлы.')
