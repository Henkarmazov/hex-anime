import os
from flask import Flask, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from scrapers.home import latest_update
from scrapers.anime import anime_filter, anime_detail
from scrapers.watch import watch_anime
from scrapers.search import search_anime
from scrapers.categories import (
    genre_list, director_list, producer_list,
    studio_list, season_list, cast_list,
)

load_dotenv()

app = Flask(__name__)
CORS(app)

# Path absolut agar Vercel bisa menemukan file HTML
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── DOCUMENTATION ─────────────────────────────────────────────
@app.route("/documentation")
def documentation():
    return send_file(os.path.join(BASE_DIR, "templates", "documentation.html"))

# ── CORE ──────────────────────────────────────────────────────
@app.route("/")
def _latest_update():
    return latest_update()

@app.route("/anime")
def _anime_filter():
    return anime_filter()

@app.route("/anime/<path:slug>")
def _anime_detail(slug):
    return anime_detail(slug)

@app.route("/ntn/<path:slug>")
def _watch_anime(slug):
    return watch_anime(slug)

@app.route("/search/<int:page>/<query>")
def _search_anime(page, query):
    return search_anime(page, query)

# ── CATEGORIES ────────────────────────────────────────────────
@app.route("/genres/<slug>", defaults={"page": 1})
@app.route("/genres/<slug>/page/<int:page>")
def _genre_list(slug, page):
    return genre_list(slug, page)

@app.route("/director/<n>", defaults={"page": 1})
@app.route("/director/<n>/page/<int:page>")
def _director_list(n, page):
    return director_list(n, page)

@app.route("/producer/<n>", defaults={"page": 1})
@app.route("/producer/<n>/page/<int:page>")
def _producer_list(n, page):
    return producer_list(n, page)

@app.route("/studio/<n>", defaults={"page": 1})
@app.route("/studio/<n>/page/<int:page>")
def _studio_list(n, page):
    return studio_list(n, page)

@app.route("/season/<n>")
def _season_list(n):
    return season_list(n)

@app.route("/cast/<n>/page/<int:page>")
def _cast_list(n, page):
    return cast_list(n, page)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
