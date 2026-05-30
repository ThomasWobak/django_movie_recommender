from django.shortcuts import render, get_object_or_404
from .models import Movie, SimilarityResult


def search_view(request):
    return render(request, 'recommender/search.html')


def search_results_view(request):
    query = request.GET.get('q', '')
    movies = []

    if query:
        movies = Movie.objects.filter(title__icontains=query).order_by('-popularity')[:50]

    context = {
        'query': query,
        'movies': movies,
    }
    return render(request, 'recommender/results.html', context)


def recommendations_view(request, movie_id):
    reference_movie = get_object_or_404(Movie, movielens_id=movie_id)

    similarities = SimilarityResult.objects.filter(
        source_movie=reference_movie
    ).select_related('target_movie').order_by('strategy_name', 'rank')

    strategies_dict = {}
    for sim in similarities:
        if sim.strategy_name not in strategies_dict:
            strategies_dict[sim.strategy_name] = []
        strategies_dict[sim.strategy_name].append(sim.target_movie)

    context = {
        'reference_movie': reference_movie,
        'strategies': strategies_dict,
    }
    return render(request, 'recommender/recommendations.html', context)