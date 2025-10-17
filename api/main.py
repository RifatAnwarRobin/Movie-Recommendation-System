from fastapi import FastAPI
#hybrid_recommendion function import as that function is defined in routers/recommendations.py
from api.routers import recommendations

app = FastAPI(
    title="Movie Recommendation System API",
    description="Hybrid movie recommendations using genre similarity and SVD.",
    version="1.0.0"
)

app.include_router(recommendations.router,prefix="/api")