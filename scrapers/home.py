from flask import jsonify
from .helpers import fetch_soup, get_slug
import os

SITE_NAME = os.getenv("SITE_NAME", "MyAnimeSite")
BASE_URL = "https://samehadaku.li/"


def latest_update():
    try:
        soup, _ = fetch_soup(BASE_URL)

        results = []
        for article in soup.select("article.bs"):
            a_tag = article.select_one("a")
            if not a_tag:
                continue

            url = a_tag.get("href", "")
            slug = get_slug(url)
            title_tag = article.select_one("h2")
            title = title_tag.get_text(strip=True) if title_tag else ""
            episode = article.select_one(".epx")
            anime_type = article.select_one(".typez")
            sub_status = article.select_one(".sb")
            image = article.select_one("img")

            results.append({
                "title_short": title,
                "title_full": title,
                "episode": episode.get_text(strip=True) if episode else "",
                "type": anime_type.get_text(strip=True) if anime_type else "",
                "status": sub_status.get_text(strip=True) if sub_status else "",
                "url": url,
                "slug": slug,
                "image": image.get("src") if image else None,
            })

        return jsonify({
            "source": BASE_URL,
            "count": len(results),
            "latest_release": results[:16],
            "recommendation": results[16:],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
