# Django Movie Recommender System

> **Course Project:** Alpen-Adria-Universität Klagenfurt
> **Course:** Information Search & Recommendation Systems (Summer Semester 2026)

This project is a Django-based movie recommendation engine. It ingests movie metadata, TMDB posters, and MovieLens datasets into a PostgreSQL database, and computes various similarity metrics (Baseline Heuristics, Genome Similarity, and TF-IDF Plot Similarity) to generate item-item recommendations.

---

## Prerequisites

Before running the project, ensure that you have the following installed and downloaded:

* **PostgreSQL**
* **Python 3.8+**
* **Required Datasets:**
  * [MovieLens 20M Dataset](https://grouplens.org/datasets/movielens/) (or a similar dataset with genome scores). Specifically:
    * `links.csv`
    * `movies_metadata.csv`
    * `genome-scores.csv`
  * [TMDB Kaggle Dataset](https://www.kaggle.com/datasets/alanvourch/tmdb-movies-daily-updates) (for the poster paths)
  * [Additional Movie Information](https://drive.google.com/file/d/1je77e0Lq8naVUsjoOzk5RuI2H3ceHlSz/view) (JSON files)

> **Important Filepath Configuration:**
> Currently, the filepaths in the scripts are hardcoded local paths. Before running any commands, you must open the following files and update the `base_dir` and/or `json_dir` variables to point to where the datasets are stored locally on your machine:
> * `load_movie_data.py`
> * `fix_posters.py`
> * `calc_genome_similarity.py`

---

## Setup & Installation

### 1. Database Setup (PostgreSQL)
Open your `settings.py` file and update the database credentials at **lines 76-86** to match your local instance of PostgreSQL.

### 2. Environment Setup
Install the required Python packages using pip:

```bash
pip install django psycopg2-binary pandas numpy scikit-learn
```

### 3. Django Initialization
Run the following Django setup commands to build the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Execution Pipeline

### 4. Data Ingestion Pipeline
The data must be loaded in a specific order to satisfy the database relations and ensure data integrity. Run the following Django management commands in this exact sequence:

```bash
python manage.py load_movie_data
python manage.py fix_posters
```

### 5. Calculate Similarities
Once the data is ingested, you need to calculate the item-item similarities. The system uses three different strategies, which can be executed in any order. 

Here are the commands, listed in order of computational complexity (from lowest to highest):

```bash
python manage.py calc_baseline_heuristic
python manage.py calc_genome_similarity
python manage.py calc_plot_similarities
```

### 6. Running the Server
Once the database is populated and similarities are calculated, you can start the development server:

```bash
python manage.py runserver
```

Navigate to http://127.0.0.1:8000/ in your web browser to view the application.


>formatting done by Google Gemini. Text written by myself
