# Movie Recommendation System

## Summary
A modular movie recommendation system with API and web interfaces. Implements collaborative filtering, content-based, and hybrid approaches with preprocessing pipelines, trained models, and multiple deployment options.

## Philosophy
- Separation of concerns: data preprocessing, ML models, API, and web UI are independent modules.
- Production-ready: includes both API (FastAPI) and interactive web interface (Streamlit).
- Reproducible pipelines: notebooks document preprocessing and model training; serialized models enable consistent predictions.
- Extensible architecture: easily swap algorithms or add new recommendation methods.

## Repository Layout
```
Movie-Recommendation-System/
├── README.md
├── requirements.txt
├── run_all.py                    # orchestrates full pipeline
├── data/
│   ├── raw/mov_lens_small/      # original MovieLens dataset
│   │   ├── movies.csv
│   │   ├── ratings.csv
│   │   ├── tags.csv
│   │   └── links.csv
│   └── processed/               # cleaned & merged datasets
│       ├── cleaned_data_final.csv
│       └── processed_merged_data.csv
├── core/
│   ├── ml_models/               # trained models & metadata
│   │   ├── model.ipynb
│   │   ├── movie_recom_svd_model.pkl
│   │   ├── movie_titles.pkl
│   │   └── movie_genres.pkl
│   └── pre_processing/          # data cleaning notebooks & diagnostics
│       ├── data_preprocess.ipynb
│       └── *.png (correlation heatmaps)
├── api/
│   ├── main.py                  # FastAPI application
│   ├── routers/
│   │   └── recommendations.py   # recommendation endpoints
│   └── schemas/
├── web/
│   └── streamlit_app.py         # interactive web interface
└── .gitignore
```

## Quick Start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the full pipeline:
```bash
python run_all.py
```
3. Access the system:
    - **API**: `python api/main.py` then visit `http://localhost:8000/docs`
    - **Web UI**: `streamlit run web/streamlit_app.py`

## Data & Models
- **Input**: MovieLens dataset (movies, ratings, tags)
- **Preprocessing**: `core/pre_processing/data_preprocess.ipynb`
- **Models**: SVD-based collaborative filtering, stored as pickled objects in `core/ml_models/`

## Development
- Add new algorithms in `core/ml_models/`
- Extend API endpoints in `api/routers/`
- Update Streamlit UI in `web/streamlit_app.py`

## License
MIT
