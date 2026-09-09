from flask import Flask, jsonify, render_template, request
from recommender import AnimeRecommender
import os
app = Flask(__name__)
recommender = AnimeRecommender("anime.csv")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/anime")
def anime_list():
    q = request.args.get("q", "").strip()
    limit = min(int(request.args.get("limit", 10)), 20)
    return jsonify(recommender.search(q, limit))

@app.get("/api/recommend")
def recommend():
    name = request.args.get("name", "").strip()
    top_n = min(max(int(request.args.get("top_n", 10)), 1), 20)
    threshold = float(request.args.get("threshold", 0.0))

    if not name:
        return jsonify({"error": "Please provide an anime name."}), 400

    try:
        result = recommender.recommend(name, top_n=top_n, threshold=threshold)
        return jsonify({"query": name, "recommendations": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
