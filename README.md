# AnimeMatch — Anime Recommendation System

A deployable Flask web app built from the supplied Anime Recommendation System notebook.

## Model used

The notebook uses:
- `TfidfVectorizer(stop_words='english')` on `genre`
- `MinMaxScaler` on `rating` and `members`
- sparse feature combination
- cosine similarity
- top-N recommendation and optional similarity threshold

This production version keeps the same feature logic but computes the similarity vector only for the selected anime instead of materializing the full 12,294 × 12,294 matrix.

## Files

- `app.py` — Flask API + web server
- `recommender.py` — recommendation engine
- `anime.csv` — **copy your dataset here**
- `templates/index.html` — frontend
- `static/style.css` — styling
- `static/app.js` — search/autocomplete/results
- `requirements.txt` — dependencies
- `Procfile` — Render/Railway-style start command

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

## Deploy on Render

1. Push this project to GitHub.
2. Create a new **Web Service** on Render.
3. Connect the GitHub repository.
4. Build command:
   `pip install -r requirements.txt`
5. Start command:
   `gunicorn app:app`
6. Deploy.

Make sure `anime.csv` is committed to the repository or replace it with cloud/object storage if the file becomes too large.

## API

`GET /api/anime?q=naruto&limit=10`

`GET /api/recommend?name=Naruto&top_n=10`

Optional threshold:

`GET /api/recommend?name=Naruto&top_n=10&threshold=0.4`
