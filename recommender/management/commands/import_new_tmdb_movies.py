import os
import ast
import pandas as pd
from django.core.management.base import BaseCommand
from recommender.models import Movie
from django.db.models import Max

class Command(BaseCommand):
    help = 'Imports new movies along with metadata from the TMDB dataset'

    def handle(self, *args, **kwargs):
        base_dir = r"C:\Users\User\Desktop\Uni\Master\Semester2\Information_Search_Recommendation_System\Exercise3\ml-1m\ml-1m"
        csv_path = os.path.join(base_dir, 'TMDB_all_movies.csv')
        links_path = os.path.join(base_dir, 'links.csv')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"Could not find dataset at {csv_path}"))
            return

        self.stdout.write("Loading links.csv to identify existing TMDB IDs...")
        links_df = pd.read_csv(links_path)
        links_df = links_df.dropna(subset=['tmdbId'])
        existing_tmdb_ids = set(links_df['tmdbId'].astype(int))

        self.stdout.write("Loading TMDB Kaggle dataset...")
        df = pd.read_csv(csv_path)

        max_ml_id = Movie.objects.aggregate(Max('movielens_id'))['movielens_id__max']
        if not max_ml_id:
            max_ml_id = 1000000
        current_new_id = max_ml_id + 1

        movies_to_create = []
        base_url = "https://image.tmdb.org/t/p/w500"

        self.stdout.write("Parsing data and extracting rich metadata...")
        for index, row in df.iterrows():
            try:
                tmdb_id = int(row['id'])
            except (ValueError, TypeError):
                continue

            if tmdb_id in existing_tmdb_ids:
                continue

            title = str(row['title']) if pd.notna(row['title']) else ""
            if not title:
                continue

            year = None
            if pd.notna(row['release_date']):
                try:
                    year_str = str(row['release_date']).strip()
                    if year_str:
                        year = int(year_str[:4])
                except ValueError:
                    pass

            popularity_score = 0
            if pd.notna(row['vote_count']):
                try:
                    popularity_score = int(row['vote_count'])
                except ValueError:
                    pass

            average_rating = 0.0
            if pd.notna(row['vote_average']):
                try:
                    average_rating = float(row['vote_average'])
                except ValueError:
                    pass

            genres_str = str(row['genres']) if pd.notna(row['genres']) else ""
            plot = str(row['overview']) if pd.notna(row['overview']) else ""

            poster_url = ""
            if pd.notna(row['poster_path']):
                relative_path = str(row['poster_path']).strip()
                if relative_path:
                    if not relative_path.startswith('/'):
                        relative_path = '/' + relative_path
                    poster_url = f"{base_url}{relative_path}"

            actors_list = []
            cast_col = 'cast' if 'cast' in df.columns else ('actors' if 'actors' in df.columns else None)
            if cast_col and pd.notna(row[cast_col]):
                try:
                    cast_data = ast.literal_eval(str(row[cast_col]))
                    if isinstance(cast_data, list):
                        for actor in cast_data[:5]:
                            if isinstance(actor, dict) and 'name' in actor:
                                actors_list.append(actor['name'])
                            elif isinstance(actor, str):
                                actors_list.append(actor)
                except Exception:
                    pass
            actors_str = ", ".join(actors_list)

            directors_list = []
            crew_col = 'crew' if 'crew' in df.columns else ('directors' if 'directors' in df.columns else ('director' if 'director' in df.columns else None))
            if crew_col and pd.notna(row[crew_col]):
                try:
                    crew_data = ast.literal_eval(str(row[crew_col]))
                    if isinstance(crew_data, list):
                        for member in crew_data:
                            if isinstance(member, dict) and member.get('job') == 'Director':
                                directors_list.append(member.get('name', ''))
                    elif isinstance(crew_data, str):
                        directors_list.append(crew_data)
                except Exception:
                    pass
            directors_str = ", ".join([d for d in directors_list if d])

            reviews_str = ""
            reviews_col = 'reviews' if 'reviews' in df.columns else None
            if reviews_col and pd.notna(row[reviews_col]):
                reviews_str = str(row[reviews_col])

            movie = Movie(
                movielens_id=current_new_id,
                title=title[:255],
                year=year,
                popularity=popularity_score,
                average_rating=average_rating,
                genres=genres_str[:255],
                plot=plot,
                poster_url=poster_url,
                actors=actors_str,
                directors=directors_str[:255],
                reviews=reviews_str
            )
            movies_to_create.append(movie)
            current_new_id += 1

        self.stdout.write(f"Inserting {len(movies_to_create)} detailed movie records into PostgreSQL...")
        Movie.objects.bulk_create(movies_to_create, batch_size=5000)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(movies_to_create)} new movies.'))