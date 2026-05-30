import os
import pandas as pd
from django.core.management.base import BaseCommand
from recommender.models import Movie


class Command(BaseCommand):
    help = 'Updates movie poster URLs using the new TMDB Kaggle dataset'

    def handle(self, *args, **kwargs):
        base_dir = r"C:\Users\User\Desktop\Uni\Master\Semester2\Information_Search_Recommendation_System\Exercise3\ml-1m\ml-1m"
        csv_path = os.path.join(base_dir, 'TMDB_all_movies.csv')
        links_path = os.path.join(base_dir, 'links.csv')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"Could not find dataset at {csv_path}"))
            return

        self.stdout.write("Loading links.csv to map MovieLens IDs to TMDB IDs...")
        links_df = pd.read_csv(links_path)
        links_df = links_df.dropna(subset=['tmdbId', 'movieId'])

        tmdb_to_ml = dict(zip(links_df['tmdbId'].astype(int), links_df['movieId'].astype(int)))

        self.stdout.write("Loading TMDB Kaggle dataset into memory...")
        df = pd.read_csv(csv_path, usecols=['id', 'poster_path'])
        df = df.dropna(subset=['poster_path'])

        poster_lookup = dict(zip(df['id'].astype(int), df['poster_path']))

        ml_to_poster = {}
        for tmdb_id, path in poster_lookup.items():
            if tmdb_id in tmdb_to_ml:
                ml_to_poster[tmdb_to_ml[tmdb_id]] = path

        self.stdout.write("Fetching movies from the database...")
        db_movies = Movie.objects.all()

        movies_to_update = []
        base_url = "https://image.tmdb.org/t/p/w500"

        self.stdout.write("Matching database records with fresh poster paths...")
        for movie in db_movies:
            try:
                ml_id_int = int(movie.movielens_id)
                if ml_id_int in ml_to_poster:
                    relative_path = ml_to_poster[ml_id_int]

                    if not relative_path.startswith('/'):
                        relative_path = '/' + relative_path

                    new_url = f"{base_url}{relative_path}"

                    if movie.poster_url != new_url:
                        movie.poster_url = new_url
                        movies_to_update.append(movie)
            except (ValueError, TypeError):
                continue

        if movies_to_update:
            self.stdout.write(f"Updating {len(movies_to_update)} records in PostgreSQL...")
            Movie.objects.bulk_update(movies_to_update, ['poster_url'], batch_size=5000)
            self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(movies_to_update)} movie posters!"))
        else:
            self.stdout.write(self.style.WARNING("No poster URL updates were necessary."))