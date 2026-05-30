import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.core.management.base import BaseCommand
from recommender.models import Movie, SimilarityResult


class Command(BaseCommand):
    help = 'Calculates Item-Item Cosine Similarity using MovieLens Genome Scores'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Genome-Similarity results...")
        SimilarityResult.objects.filter(strategy_name="Genome-Similarity").delete()

        base_dir = r"C:\Users\User\Desktop\Uni\Master\Semester2\Information_Search_Recommendation_System\Exercise3\ml-1m\ml-1m"
        genome_path = os.path.join(base_dir, 'genome-scores.csv')

        if not os.path.exists(genome_path):
            self.stdout.write(self.style.ERROR(f"Could not find {genome_path}. Please ensure the file is present."))
            return

        self.stdout.write("Loading genome scores into memory (this may take a moment)...")
        # Load the scores and pivot into a matrix: Rows = movieId, Columns = tagId
        genome_df = pd.read_csv(genome_path)
        pivot_df = genome_df.pivot(index='movieId', columns='tagId', values='relevance')

        pivot_df = pivot_df.fillna(0)

        self.stdout.write("Fetching movies from PostgreSQL database...")
        db_movies = {m.movielens_id: m for m in Movie.objects.all()}

        # Filter the pandas dataframe to ONLY include movies that actually exist in our database
        valid_movie_ids = list(set(pivot_df.index).intersection(set(db_movies.keys())))
        filtered_pivot_df = pivot_df.loc[valid_movie_ids]


        index_to_movielens_id = filtered_pivot_df.index.tolist()

        self.stdout.write(f"Calculating Cosine Similarity matrix for {len(valid_movie_ids)} movies...")
        sim_matrix = cosine_similarity(filtered_pivot_df)

        results_to_create = []

        self.stdout.write("Extracting top 5 semantic matches per movie...")
        # Iterate through the similarity matrix
        for idx, row in enumerate(sim_matrix):
            source_ml_id = index_to_movielens_id[idx]
            source_movie = db_movies[source_ml_id]

            # argsort() sorts ascending. We want descending, so we take the last 6 elements (including itself)
            # and reverse it using [::-1]
            top_indices = np.argsort(row)[-6:][::-1]

            rank = 1
            for target_idx in top_indices:
                target_ml_id = index_to_movielens_id[target_idx]

                if source_ml_id == target_ml_id:
                    continue

                # Stop if we already found 5
                if rank > 5:
                    break

                target_movie = db_movies[target_ml_id]

                results_to_create.append(SimilarityResult(
                    source_movie=source_movie,
                    target_movie=target_movie,
                    strategy_name="Genome-Similarity",
                    rank=rank
                ))
                rank += 1

        self.stdout.write(f"Inserting {len(results_to_create)} similarity records into PostgreSQL...")

        chunk_size = 5000
        for i in range(0, len(results_to_create), chunk_size):
            SimilarityResult.objects.bulk_create(results_to_create[i:i + chunk_size])

        self.stdout.write(self.style.SUCCESS('Successfully calculated Genome-Similarity recommendations.'))