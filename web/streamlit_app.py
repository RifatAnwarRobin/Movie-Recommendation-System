import streamlit as st
import requests #type: ignore
import time
from urllib.parse import quote

#API endpoint from FastAPI backend
API_URL = "http://localhost:8000/api/recommend"
def check_api_available():
    """Check if the API is available"""
    try:
        response = requests.get("http://localhost:8000/recommend?movie_title=test&top_n=1")
        return True
    except:
        return False
    
#Streamlit UI
st.title("🎬 Movie Recommender")
movie_title = st.text_input("Enter a movie title:", "Toy Story")
top_n = st.slider("Number of recommendations:", 1, 10)

if st.button("Get Recommendations"):
    with st.spinner("Fetching recommendations for you 😁..."):
        try:
            encoded_title = quote(movie_title)
            response = requests.get(f"{API_URL}?movie_title={encoded_title}&top_n={top_n}", timeout=300)

            if response.status_code == 200:
                recommendations = response.json()

                #either valid recommendations or an error message
                if recommendations and isinstance(recommendations[0], str) and recommendations[0].startswith("Sorry") or recommendations[0].startswith("We couldn't"):
                    st.warning(recommendations[0])
                else:
                    st.success(f"Recommendations for **{movie_title}**:")
                    for idx, movie in enumerate(recommendations, 1):
                        st.write(f"{idx}. {movie}")
            else:
                st.warning("We couldn't process your request. Please try again.")

        except requests.exceptions.RequestException as e:
            st.warning("We're having trouble connecting to the recommendation service. Please try again later.")
