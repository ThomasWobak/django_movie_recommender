from django.db import models

class Movie(models.Model):
    movielens_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    plot = models.TextField(blank=True)
    poster_url = models.URLField(max_length=500, blank=True)
    popularity = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    genres = models.CharField(max_length=255, blank=True)
    actors = models.CharField(max_length=500, blank=True)
    directors = models.CharField(max_length=255, blank=True)
    reviews = models.TextField(blank=True)

class SimilarityResult(models.Model):
    source_movie = models.ForeignKey(Movie, related_name='similarities', on_delete=models.CASCADE)
    target_movie = models.ForeignKey(Movie, related_name='recommended_for', on_delete=models.CASCADE)
    strategy_name = models.CharField(max_length=50)
    rank = models.IntegerField()