from collections import defaultdict
from django.core.management.base import BaseCommand
from recommender.models import Movie, SimilarityResult


class Command(BaseCommand):
    help = 'Calculates similar movies based on partial genre overlap and popularity'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Genre-Overlap results...")
        SimilarityResult.objects.filter(strategy_name="Genre-Overlap").delete()

        self.stdout.write("Fetching movies from database...")
        movies = list(Movie.objects.only('id', 'genres', 'popularity'))

        movie_data = {}
        genre_index = defaultdict(list)

        self.stdout.write("Building genre index...")
        for m in movies:
            if m.genres:
                g_set = set([g.strip() for g in m.genres.split(',') if g.strip()])
                movie_data[m.id] = {'genres': g_set, 'popularity': m.popularity, 'obj': m}

                for g in g_set:
                    genre_index[g].append(m.id)

        results_to_create = []

        self.stdout.write("Calculating overlaps...")

        for source_id, data in movie_data.items():
            source_genres = data['genres']

            overlap_counts = defaultdict(int)
            for g in source_genres:
                for target_id in genre_index[g]:
                    if target_id != source_id:
                        overlap_counts[target_id] += 1

            candidates = []
            for target_id, overlap in overlap_counts.items():
                candidates.append((target_id, overlap, movie_data[target_id]['popularity']))

            candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
            top_5 = candidates[:5]

            for rank, (target_id, overlap, _) in enumerate(top_5, start=1):
                results_to_create.append(SimilarityResult(
                    source_movie=data['obj'],
                    target_movie=movie_data[target_id]['obj'],
                    strategy_name="Genre-Overlap",
                    rank=rank
                ))

        self.stdout.write(f"Inserting {len(results_to_create)} similarity records into PostgreSQL...")
        SimilarityResult.objects.bulk_create(results_to_create, batch_size=5000)

        self.stdout.write(self.style.SUCCESS('Successfully calculated Genre-Overlap baseline.'))