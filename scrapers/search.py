from flask import jsonify
from .helpers import fetch_soup, scrape_article_bs, scrape_pagination

BASE_URL = "https://samehadaku.li/"


def search_anime(page, query):
    try:
        url = f"{BASE_URL}page/{page}/?s={query}"
        soup, _ = fetch_soup(url)

        search_title = ""
        title_box = soup.select_one("div.releases h1 span")
        if title_box:
            search_title = title_box.get_text(strip=True)

        results = []
        for article in soup.select("article.bs"):
            item = scrape_article_bs(article)
            if item:
                results.append(item)

        pagination = scrape_pagination(soup, page)

        return jsonify({
            "source": url,
            "query": query,
            "search_title": search_title,
            "page": page,
            "pagination": pagination,
            "results": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
