import os, pickle

files = [
    "core/ml_models/movie_genres.pkl",
    "core/ml_models/movie_recom_svd_model.pkl",
    "core/ml_models/movie_titles.pkl"
]

for f in files:
    if not os.path.exists(f):
        raise FileNotFoundError(f"{f} is missing!")
    pickle.load(open(f, "rb"))

print("All ML models loaded successfully.")