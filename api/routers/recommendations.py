import pickle
import numpy as np
from typing import List
from fastapi import APIRouter, HTTPException
#try to find closest match
from fuzzywuzzy import fuzz #type: ignore
import pandas as pd #type: ignore
#load the ratings data for fallback popular movie recommendations
df = pd.read_csv('E://Coding/ML_projects/Movie-Recommendation-System/data/processed/cleaned_data_final.csv')

#loading models and prepared data
try:
    with open('E://Coding/ML_projects/Movie-Recommendation-System/core/ml_models/movie_recom_svd_model.pkl', 'rb') as f:
        svd_model = pickle.load(f)

    with open('E://Coding/ML_projects/Movie-Recommendation-System/core/ml_models/movie_genres.pkl', 'rb') as f:
        movie_genres = pickle.load(f)

    with open('E://Coding/ML_projects/Movie-Recommendation-System/core/ml_models/movie_titles.pkl', 'rb') as f:
        movie_titles = pickle.load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load models: {e}")


def jaccard_similarity(a:np.ndarray, b:np.ndarray)-> float:
    """Let's talk about Jaccard Similarity for genre-based filtering.
    Jaccard similarity measures the similarity between two sets by dividing the size of their intersection by the size of their union.
    so jaccard(A, B) = |A ∩ B| / |A ∪ B|.
    it ranges from 0 to 1, where 0 means no similarity and 1 means identical sets.
    In the context of movie recommendations, we can represent each movie's genres as a binary vector, where each genre corresponds to a dimension in the vector. A value of 1 indicates the presence of a genre, while 0 indicates its absence.
    By calculating the Jaccard similarity between the genre vectors of different movies, we can identify movies that share similar genres.
    This allows us to recommend movies that are more likely to align with a user's preferences based on genre similarity.
    """
    #as 0 and 1 are used for genre presence, we can use numpy to find indices of genres present in both movies
    set_a = set(np.where(a == 1)[0])#this will give the indices of genres present in movie a
    set_b = set(np.where(b == 1)[0])#this will give the indices of genres present in movie b
    
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    
    #jaccard(A, B) = |A ∩ B| / |A ∪ B|
    return intersection / union if union != 0 else 0

def hybrid_recommend(movie_title:str, top_n:int =10)-> List[str]:
    #find the given movie index
    try:
        idx = np.where(movie_titles == movie_title)[0][0]
        target_genres = movie_genres[idx]
    except IndexError:
        # raise HTTPException(status_code=404, detail="Movie not found, please check the title and try again.")
        pass #as no need to show error to the client directly, instead give message in response
    
    #while testing, found that the searched movie title should match properly to get recommendation.
    #so,will try fuzzy matching to reduce such issues amap(as much as possible :P)
    if 'idx' not in locals():
        matches = []
        for ind, title in enumerate(movie_titles):
            score = fuzz.ratio(movie_title.lower(), title.lower())
            print(f"Fuzzy score for '{movie_title}' and '{title}': {score}")
            if score > 80:  #80% similarity threshold
                matches.append((ind, title, score))
                
        print(f"Fuzzy-matches found: {matches}")
        if matches:
            best_match = max(matches, key=lambda x: x[2])
            idx = best_match[0]
            target_genres = movie_genres[idx]
            movie_title = best_match[1]#use the corrected title
        else:
            return ["Sorry, we couldn't find that movie. Please check the spelling and try again."]
    
    #compute Jaccard similarity with all movies    
    all_similarities = []
    for i, genres in enumerate(movie_genres):
        if i == idx:  # Skip the input movie itself
            continue
        sim = jaccard_similarity(target_genres, genres)
        all_similarities.append((i, sim))

    #sort by similarity and get all candidates
    all_similarities.sort(key=lambda x: x[1], reverse=True)
    print(f"all similar movies (by Jaccard): {all_similarities[:10]}")

    #unique movie indices
    unique_recs = set()
    final_recommendations = []

    #keep adding recommendations until we have enough unique ones
    for i, sim in all_similarities:
        movie_idx = i
        movie = movie_titles[movie_idx]

        #skip if we already have this movie
        if movie in unique_recs or movie == movie_title:
            continue

        #appendd to the recommendations
        unique_recs.add(movie)
        final_recommendations.append((movie_idx, sim))

        #stop when have enough
        if len(unique_recs) >= top_n:
            break

    #get more candidates if needed to fill top_n requirement
    if len(unique_recs) < top_n:
        #can get more by lowering the similarity threshold
        for i, sim in all_similarities[len(final_recommendations):]:
            movie_idx = i
            movie = movie_titles[movie_idx]
            print(f"Checking additional movie: {movie} with similarity {sim}")
            if movie not in unique_recs:
                unique_recs.add(movie)
                final_recommendations.append((movie_idx, sim))

                if len(unique_recs) >= top_n:
                    break

    #rank by SVD predictions
    predictions = []
    for movie_idx, sim in final_recommendations:
        try:
            pred = svd_model.predict(uid=0, iid=movie_idx+1).est
            predictions.append((movie_idx, pred))
        except:
            continue

    #sort by predicted rating from svd mdoel
    predictions.sort(key=lambda x: x[1], reverse=True)

    #final unique movie titles
    result = []
    seen = set()
    for movie_idx, pred in predictions:
        movie = movie_titles[movie_idx]
        if movie not in seen:
            seen.add(movie)
            result.append(movie)
            if len(result) >= top_n:
                break
    print(f"Seened movies: {seen}")
    
    #this will act as a fallback if not enough recommendations found
    if len(result) < top_n:
        #fetched top rated movies from the dataset
        if 'rating_scaler' in df.columns:
            top_movies = df.groupby('movieId')['rating_scaler'].mean().sort_values(ascending=False).head(50)
            top_movie_ids = top_movies.index.tolist()

            for movie_id in top_movie_ids:
                if movie_id-1 in [i for i, _ in final_recommendations]:
                    continue  #skip already recommended ones

                movie_idx = movie_id-1
                movie = movie_titles[movie_idx]
                if movie not in seen:
                    seen.add(movie)
                    result.append(movie)
                    if len(result) >= top_n:
                        break

    return result if result else ["Sorry, we couldn't find enough recommendations. Try a different movie!"]

router = APIRouter()

@router.get("/recommend", response_model=List[str])
async def recommend(movie_title:str, top_n: int=10):
    return hybrid_recommend(movie_title, top_n)
