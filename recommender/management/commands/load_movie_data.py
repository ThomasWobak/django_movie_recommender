import os
import json
import ast
import pandas as pd
from django.core.management.base import BaseCommand
from recommender.models import Movie


class Command(BaseCommand):
    help = 'Loads movie data from CSVs and supplementary JSON files'

    def handle(self, *args, **kwargs):
        base_dir = r"C:\Users\User\Desktop\Uni\Master\Semester2\Information_Search_Recommendation_System\Exercise3\ml-1m\ml-1m"
        json_dir = r"C:\Users\User\Desktop\Uni\Master\Semester2\Information_Search_Recommendation_System\Exercise3\ml-1m\extracted_content_ml-latest"

        self.stdout.write("Parsing JSON files...")
        json_metadata = {}
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(json_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ml_id = data.get('movielensId')

                    if ml_id:
                        ml_data = data.get('movielens') or {}
                        tmdb_data = data.get('tmdb') or {}
                        imdb_data = data.get('imdb') or {}

                        actors_list = ml_data.get('actors') or []
                        directors_list = ml_data.get('directors') or []
                        reviews_list = imdb_data.get('reviews') or []

                        json_metadata[int(ml_id)] = {
                            'plot': ml_data.get('plotSummary') or tmdb_data.get('overview') or '',
                            'poster_path': ml_data.get('posterPath') or tmdb_data.get('poster_path') or '',
                            'year': ml_data.get('releaseYear'),
                            'num_ratings': ml_data.get('numRatings') or tmdb_data.get('vote_count') or 0,
                            'avg_rating': ml_data.get('avgRating') or tmdb_data.get('vote_average') or 0.0,
                            'actors': ", ".join(actors_list[:10]),
                            'directors': ", ".join(directors_list),
                            'reviews': json.dumps(reviews_list[:5])
                        }

        self.stdout.write("Loading links.csv...")
        links_path = os.path.join(base_dir, 'links.csv')
        links_df = pd.read_csv(links_path)
        links_df = links_df.dropna(subset=['tmdbId', 'movieId'])
        tmdb_to_ml = dict(zip(links_df['tmdbId'].astype(int).astype(str), links_df['movieId'].astype(int)))

        self.stdout.write("Loading movies_metadata.csv...")
        metadata_path = os.path.join(base_dir, 'movies_metadata.csv')
        metadata_df = pd.read_csv(metadata_path, low_memory=False, on_bad_lines='skip')

        self.stdout.write("Clearing existing database records...")
        Movie.objects.all().delete()

        movies_to_create = []
        seen_ml_ids = set()

        self.stdout.write("Preparing database objects...")
        for index, row in metadata_df.iterrows():
            tmdb_id = str(row['id'])
            if tmdb_id not in tmdb_to_ml:
                continue

            movie_id = tmdb_to_ml[tmdb_id]

            if movie_id in seen_ml_ids:
                continue

            seen_ml_ids.add(movie_id)

            title = str(row['title']) if pd.notna(row['title']) else ""

            meta = json_metadata.get(movie_id, {})

            year = meta.get('year')
            if year:
                try:
                    year = int(year)
                except ValueError:
                    year = None
            else:
                year = None

            if not year and pd.notna(row.get('release_date')):
                try:
                    year_str = str(row['release_date']).strip()
                    if year_str:
                        year = int(year_str[:4])
                except ValueError:
                    year = None

            popularity_score = meta.get('num_ratings', 0)
            if not popularity_score and pd.notna(row.get('vote_count')):
                try:
                    popularity_score = int(row['vote_count'])
                except ValueError:
                    pass

            average_rating = meta.get('avg_rating', 0.0)
            if not average_rating and pd.notna(row.get('vote_average')):
                try:
                    average_rating = float(row['vote_average'])
                except ValueError:
                    pass

            genres_str = ""
            try:
                if pd.notna(row['genres']):
                    genres_list = ast.literal_eval(row['genres'])
                    genres_str = ", ".join([g['name'] for g in genres_list])
            except (ValueError, SyntaxError):
                pass

            plot = meta.get('plot', str(row.get('overview', '')))

            poster_path = meta.get('poster_path') or row.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path and pd.notna(
                poster_path) else ""

            actors = meta.get('actors', '')
            directors = meta.get('directors', '')
            reviews = meta.get('reviews', '')

            if plot and plot != 'nan':
                movie = Movie(
                    movielens_id=movie_id,
                    title=title[:255],
                    year=year,
                    popularity=popularity_score,
                    average_rating=average_rating,
                    genres=genres_str[:255],
                    plot=plot,
                    poster_url=poster_url,
                    actors=actors[:500],
                    directors=directors[:255],
                    reviews=reviews
                )
                movies_to_create.append(movie)

        self.stdout.write(f"Inserting {len(movies_to_create)} movies into PostgreSQL...")
        Movie.objects.bulk_create(movies_to_create, batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Successfully completed data ingestion.'))