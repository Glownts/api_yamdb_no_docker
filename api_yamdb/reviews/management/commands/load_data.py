from csv import DictReader
from django.core.management import BaseCommand

from reviews.models import (
    Category,
    Comment,
    GenreTitle,
    Genre,
    Review,
    Title,
    User
)


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""

DIR = './static/data/'


class Command(BaseCommand):
    '''
    Загружает данные из csv в БД.
    Если данные уже есть в БД, выдаст ошибку ALREDY_LOADED_ERROR_MESSAGE.
    '''
    help = "Loads data from .csv-files"

    def handle(self, *args, **options):

        models = (
            Category,
            Comment,
            GenreTitle,
            Genre,
            Review,
            Title,
            User
        )

        for model in models:
            if model.objects.exists():
                print(f'{model} data already exiting.')
                print(ALREDY_LOADED_ERROR_MESSAGE)
                return

        print("Loading data")

        for row in DictReader(open(DIR + 'users.csv')):
            data = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio']
            )
            data.save()

        for row in DictReader(open(DIR + 'category.csv')):
            data = Category(
                id=row['id'],
                name=row['name'],
                slug=row['slug']
            )
            data.save()

        for row in DictReader(open(DIR + 'genre.csv')):
            data = Genre(
                id=row['id'],
                name=row['name'],
                slug=row['slug']
            )
            data.save()

        for row in DictReader(open(DIR + 'titles.csv')):
            data = Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                description=row['description'],
                category_id=row['category']
            )
            data.save()

        for row in DictReader(open(DIR + 'genre_title.csv')):
            data = GenreTitle(
                id=row['id'],
                genre_id=row['genre_id'],
                title_id=row['title_id']
            )
            data.save()

        for row in DictReader(open(DIR + 'review.csv')):
            data = Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author_id=row['author'],
                score=row['score'],
                pub_date=row['pub_date']
            )
            data.save()

        for row in DictReader(open(DIR + 'comments.csv')):
            data = Comment(
                id=row['id'],
                text=row['text'],
                pub_date=row['pub_date'],
                author_id=row['author'],
                review_id=row['review_id']
            )
            data.save()
