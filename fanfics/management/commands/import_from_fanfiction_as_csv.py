import csv
import os
import re

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from fanfics.models import Fanfic
from categories.models import Category, SubCategory


class Command(BaseCommand):
    help = (
        "Import fanfictions from a local csv",
        "from external site : https://www.fanfiction.net/"
    )

    def create_subcategory(self):
        if not SubCategory.objects.filter(name="Marvel").exists():
            SubCategory.objects.get_or_create(name='Marvel', category=Category.objects.get(
                name="BD-Comics-DA"), description="Marvel Worldwide Inc., plus communément appelé Marvel Comics ou simplement Marvel, est une subdivision de Marvel Entertainment et l'une des principales maisons d'édition américaines de comics. Martin Goodman fonde la société en 1938 pour profiter de l'engouement naissant pour les comics.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = Fanfic
        self.create_subcategory()

    def find_whole_word(self, word):
        return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search

    def import_from_fanfiction_as_csv(self, data):
        try:
            rating = ""
            if data["classement"] == "Rated: T":
                rating = "r"
            elif data["classement"] == "Rated: K":
                rating = "g"
            elif data["classement"] == "Rated: K+":
                rating = "13"
            elif data["classement"] == "Rated: M":
                rating = "18"

            lang = "fr"
            if data["language"] == "English":
                lang = "en"

            genre = ["GE", "DR"]
            if self.find_whole_word('Adventure')(data["genre"]):
                genre = ["AC"]
            elif self.find_whole_word('Romance')(data["genre"]):
                genre = ["RO"]
            elif self.find_whole_word('Tragedy')(data["genre"]):
                genre = ["TR"]
            elif self.find_whole_word('Sci')(data["genre"]):
                genre = ["GE"]
            elif self.find_whole_word('Supernatural')(data["genre"]):
                genre = ["SU"]

            if not self.model_name.objects.filter(title=data["title"]).exists():
                self.model_name.objects.get_or_create(
                    title=data["title"],
                    genres=genre,
                    synopsis=data["synopsis"],
                    author=User.objects.get(username="admin"),
                    picture=data["picture"],
                    description=data["link_fanfic"],
                    link_fanfic=data["link_fanfic"],
                    language=lang,
                    classement=rating,
                    status='publié',
                    category=Category.objects.get(name="BD-Comics-DA"),
                    subcategory=SubCategory.objects.get(
                        name='Marvel'),
                    credits='Marvel Comics',
                    fanfic_is_scraped=True
                )
        except Exception as e:
            raise CommandError("Error in inserting {}: {}".format(
                self.model_name, str(e)))

    def get_current_app_path(self):
        return apps.get_app_config('fanfics').path

    def get_csv_file(self, filename):
        app_path = self.get_current_app_path()
        file_path = os.path.join(app_path, "management",
                                 "commands", filename)
        return file_path

    def add_arguments(self, parser):
        parser.add_argument('filenames',
                            nargs='+',
                            type=str,
                            help="Inserts Fanfictions from CSV file")

    def handle(self, *args, **options):
        for filename in options['filenames']:
            self.stdout.write(self.style.SUCCESS(
                'Reading:{}'.format(filename)))
            file_path = self.get_csv_file(filename)
            try:
                with open(file_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    for row in csv_reader:
                        if row != "":
                            # print(row)
                            words = [word.strip() for word in row]
                            title = words[0]
                            picture = 'https://www.fanfiction.net' + words[1]
                            author = words[2]
                            synopsis = words[3]
                            classement = words[4]
                            language = words[5]
                            genre = words[6]
                            link_fanfic = 'https://www.fanfiction.net' + \
                                words[7]
                            # print(words[7])
                            data = {}
                            data["title"] = title
                            data["picture"] = picture
                            data["author"] = author
                            data["synopsis"] = synopsis
                            data["language"] = language
                            data["classement"] = classement
                            data["link_fanfic"] = link_fanfic
                            data["genre"] = genre
                            self.import_from_fanfiction_as_csv(data)
                            self.stdout.write(
                                self.style.SUCCESS('{} - {} - {}'.format(
                                    title, classement,
                                    genre
                                )
                                )
                            )

            except FileNotFoundError:
                raise CommandError("File {} does not exist".format(
                    file_path))
