This project is for the course from the Alpen-Adria-Universität Klagenfurt, for the Course "Information Search & Recommendation Systems" during the Summer semester of 2026. 

This project is a Django-based movie recommendation engine. It ingests movie metadata, TMDB posters, and MovieLens datasets into a PostgreSQL database, and computes various similarity metrics (Baseline Heuristics, Genome Similarity, and TF-IDF Plot Similarity) to generate item-item recommendations.

Before running ensure that you have the following prerequisites: 
* PostgreSQL
* Python 3.8+
* The MovieLens Dataset 20M dataset <link: [https://drive.google.com/file/d/1je77e0Lq8naVUsjoOzk5RuI2H3ceHlSz/view](https://grouplens.org/datasets/movielens/ 
)> (or a similar dataset with genome scores). Specifically: 
  *links.csv
  *movies_metadata.csv
  *genome-scores.csv
* TMDB Kaggle Dataset <link: [https://www.kaggle.com/datasets/alanvourch/tmdb-movies-daily-updates]>(for the poster Paths):
* Additional Information about the movies in JSON files <link: [https://drive.google.com/file/d/1je77e0Lq8naVUsjoOzk5RuI2H3ceHlSz/view]

Currently the filepaths in the are hardcoded local paths. Before running any commands, you must open the following files and update the base_dir and/or json_dir variable to point to where the dataset are stored locally:
  *load_movies_data.py
  *fix_posters.py
  *calc_genome_similarity.py

1) Database Setup (PostgreSQL):
  Go into settings.py and update the credentials at line 76-86 to match your local instance of PostgreSQL. 

2) Environment Setup: 
  Install the required packages: 
  *pip install django psycopg2-binary pandas numpy scikit-learn

3) Django Initialization: 
  Run the following Django setup commands to build the databse schema: 
    python manage.py makemigrations
    python manage.py migrate

4) Data Ingestion Pipeline:
   The data must be loaded in a specific order to satisfy the database relations and ensure data integrity.
   Run the following Django Management commands in this order:
     python manage.py load_movie_data
     python manage.py fix_posters

5) Calculate Similarities:
   Once the data is ingested, you need to calculate the item-item similarities. The system uses three different strategies, which can be executed in any order.
   The commands are, in order of computational complexity:
     python manage.py calc_baseline_heuristic
     python manage.py calc_genome_similarity
     python manage.py calc_plot_similarities

6) Running the Server:
   Once the database is populated and similarities are calculated, you can start the development server:
     python manage.py runserver
   Navigate to http://127.0.0.1:8000/ in your browser to view the application
