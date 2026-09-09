import html
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


class AnimeRecommender:
    """
    Content-based recommender matching the notebook's approach:
    TF-IDF on genre + MinMax-scaled rating/members + cosine similarity.
    Unlike the notebook, it computes similarities only for the requested
    anime, avoiding a huge 12,294 x 12,294 similarity matrix in production.
    """

    def __init__(self, csv_path="anime.csv"):
        self.df = pd.read_csv(csv_path).copy()

        self.df["genre"] = self.df["genre"].fillna("Unknown").astype(str)
        self.df["type"] = self.df["type"].fillna(
            self.df["type"].mode()[0] if not self.df["type"].mode().empty else "Unknown"
        ).astype(str)
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce")
        self.df["rating"] = self.df["rating"].fillna(self.df["rating"].median())
        self.df["members"] = pd.to_numeric(self.df["members"], errors="coerce").fillna(0)

        self.tfidf = TfidfVectorizer(stop_words="english")
        genre_matrix = self.tfidf.fit_transform(self.df["genre"])

        self.scaler = MinMaxScaler()
        numeric = self.scaler.fit_transform(self.df[["rating", "members"]])

        self.features = hstack([genre_matrix, numeric]).tocsr()

        # Normalize names for friendlier matching while preserving the original name.
        self.name_to_indices = {}
        for i, name in enumerate(self.df["name"].astype(str)):
            key = " ".join(html.unescape(name).lower().split())
            self.name_to_indices.setdefault(key, []).append(i)

    def search(self, query="", limit=10):
        query = query.lower().strip()
        if not query:
            rows = self.df.head(limit)
        else:
            mask = self.df["name"].astype(str).str.lower().str.contains(
                query, regex=False, na=False
            )
            rows = self.df.loc[mask].head(limit)

        return self._records(rows)

    def _resolve_index(self, anime_name):
        key = " ".join(html.unescape(anime_name).lower().split())
        if key in self.name_to_indices:
            return self.name_to_indices[key][0]

        # Exact case-insensitive fallback.
        matches = self.df.index[
            self.df["name"].astype(str).str.lower() == anime_name.lower()
        ].tolist()
        if matches:
            return matches[0]

        raise ValueError(f'Anime "{anime_name}" was not found in anime.csv.')

    def recommend(self, anime_name, top_n=10, threshold=0.0):
        idx = self._resolve_index(anime_name)

        scores = cosine_similarity(self.features[idx], self.features).ravel()
        order = np.argsort(-scores)

        recommendations = []
        for i in order:
            if i == idx:
                continue
            score = float(scores[i])
            if score <= threshold:
                continue

            row = self.df.iloc[i]
            recommendations.append({
                "name": html.unescape(str(row["name"])),
                "genre": html.unescape(str(row["genre"])),
                "rating": round(float(row["rating"]), 2),
                "type": str(row["type"]),
                "episodes": str(row["episodes"]),
                "members": int(row["members"]),
                "similarity": round(score * 100, 1),
            })

            if len(recommendations) >= top_n:
                break

        return recommendations

    def _records(self, rows):
        result = []
        for _, row in rows.iterrows():
            result.append({
                "name": html.unescape(str(row["name"])),
                "genre": html.unescape(str(row["genre"])),
                "rating": round(float(row["rating"]), 2),
                "type": str(row["type"]),
                "episodes": str(row["episodes"]),
                "members": int(row["members"]),
            })
        return result
