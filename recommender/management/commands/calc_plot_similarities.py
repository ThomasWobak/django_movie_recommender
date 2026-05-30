import numpy as np
from django.core.management.base import BaseCommand
from recommender.models import Movie, SimilarityResult
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class Command(BaseCommand):
    help = 'Calculates Item-Item similarity based on full TF-IDF vectorization (High RAM Usage)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Plot-Similarity results...")
        SimilarityResult.objects.filter(strategy_name="Plot-Similarity").delete()

        self.stdout.write("Fetching movies with valid plots from the database...")
        movies = list(
            Movie.objects.exclude(plot__isnull=True).exclude(plot__exact='').only('id', 'movielens_id', 'plot'))

        if not movies:
            self.stdout.write(self.style.ERROR("No movies with plots found."))
            return

        plots = [movie.plot for movie in movies]

        self.stdout.write(f"Vectorizing {len(plots)} plots")
        #stop_words=english removes common words like "the"
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(plots)

        self.stdout.write("Calculating the full Cosine Similarity.")
        sim_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)

        results_to_create = []

        self.stdout.write("Extracting the top 5 matches for each movie...")
        for idx, row in enumerate(sim_matrix):
            source_movie = movies[idx]

            top_indices = np.argsort(row)[-6:][::-1]

            rank = 1
            for target_idx in top_indices:
                if idx == target_idx:
                    continue

                if rank > 5:
                    break

                target_movie = movies[target_idx]

                results_to_create.append(SimilarityResult(
                    source_movie=source_movie,
                    target_movie=target_movie,
                    strategy_name="Plot-Similarity",
                    rank=rank
                ))
                rank += 1

        self.stdout.write(f"Inserting {len(results_to_create)} similarity records into PostgreSQL...")

        db_chunk_size = 5000
        for i in range(0, len(results_to_create), db_chunk_size):
            SimilarityResult.objects.bulk_create(results_to_create[i:i + db_chunk_size])

        self.stdout.write(self.style.SUCCESS('Successfully calculated full Plot-Similarity recommendations.'))