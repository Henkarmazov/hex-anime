from flask import jsonify
from .helpers import fetch_soup, get_slug, scrape_article_bs, scrape_pagination

BASE_URL = "https://samehadaku.li/"


def _list_route(url: str, page: int, name_selector: str, article_selector: str = "article.bs") -> tuple:
    """Generic helper for listing routes with pagination."""
    soup, _ = fetch_soup(url)

    label = ""
    name_tag = soup.select_one(name_selector)
    if name_tag:
        label = name_tag.get_text(strip=True)

    results = []
    for article in soup.select(article_selector):
        item = scrape_article_bs(article)
        if item:
            results.append(item)

    pagination = scrape_pagination(soup, page)
    return soup, label, results, pagination


def genre_list(slug, page):
    try:
        url = f"{BASE_URL}genres/{slug}/page/{page}/"
        _, genre_name, results, pagination = _list_route(url, page, "div.releases h1 span")
        return jsonify({
            "source": url, "genre": genre_name, "slug": slug,
            "page": page, "pagination": pagination, "results": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def director_list(name, page):
    try:
        url = f"{BASE_URL}director/{name}/page/{page}/"
        _, director_name, results, pagination = _list_route(url, page, "div.releases h1 span")
        return jsonify({
            "source": url, "director": director_name, "slug": name,
            "page": page, "pagination": pagination, "results": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def producer_list(name, page):
    try:
        url = f"{BASE_URL}producer/{name}/page/{page}/"
        _, producer_name, results, pagination = _list_route(
            url, page, "div.releases h1 span", "div.listupd article.bs"
        )
        return jsonify({
            "source": url, "producer": producer_name, "slug": name,
            "page": page, "pagination": pagination, "results": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def studio_list(name, page):
    try:
        url = f"{BASE_URL}studio/{name}/page/{page}/"
        _, studio_name, results, pagination = _list_route(url, page, "div.releases h1 span")
        return jsonify({
            "source": url, "studio": studio_name, "slug": name,
            "page": page, "pagination": pagination, "results": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def season_list(name):
    try:
        url = f"{BASE_URL}season/{name}/"
        soup, _ = fetch_soup(url)

        season_title = ""
        title_box = soup.select_one("h1")
        if title_box:
            season_title = title_box.get_text(strip=True)

        anime_list = []
        for card in soup.select("div.card"):
            a_tag = card.select_one(".card-box a")
            if not a_tag:
                continue

            anime_url = a_tag.get("href", "")
            anime_slug = get_slug(anime_url)

            img = card.select_one(".card-thumb img")
            anime_title = card.select_one(".card-title h2")
            anime_studio = card.select_one(".card-title .studio")
            rating = card.select_one(".card-info-top .right span")

            info_top = card.select_one(".card-info-top .left")
            episodes, status, alternative = "", "", ""
            if info_top:
                ep_span = info_top.select_one("span:nth-of-type(1)")
                episodes = ep_span.get_text(strip=True) if ep_span else ""
                status_span = info_top.select_one(".status")
                status = status_span.get_text(strip=True) if status_span else ""
                alt_span = info_top.select_one(".alternative")
                alternative = alt_span.get_text(strip=True) if alt_span else ""

            desc = card.select_one(".card-info .desc")
            description = "\n".join(
                p.get_text(" ", strip=True) for p in desc.find_all("p")
            ) if desc else ""

            genres = [
                {"name": g.get_text(strip=True), "slug": get_slug(g.get("href")), "link": g.get("href")}
                for g in card.select(".card-info-bottom a")
            ]

            anime_list.append({
                "title": anime_title.get_text(strip=True) if anime_title else "",
                "studio": anime_studio.get_text(strip=True) if anime_studio else "",
                "episodes": episodes,
                "status": status,
                "alternative": alternative,
                "rating": rating.get_text(strip=True) if rating else "",
                "description": description,
                "genres": genres,
                "url": anime_url,
                "slug": anime_slug,
                "image": img.get("src") if img else None,
            })

        return jsonify({
            "source": url, "season": season_title, "slug": name, "results": anime_list,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def cast_list(name, page):
    try:
        url = f"{BASE_URL}cast/{name}/page/{page}/"
        soup, _ = fetch_soup(url)

        cast_name = ""
        title_box = soup.select_one(".releases h1 span")
        if title_box:
            cast_name = title_box.get_text(strip=True)

        anime_list = []
        for article in soup.select("div.listupd article.bs"):
            a_tag = article.select_one("a")
            if not a_tag:
                continue
            anime_url = a_tag.get("href", "")
            img = article.select_one("img")
            anime_list.append({
                "title": article.select_one(".tt").get_text(strip=True) if article.select_one(".tt") else "",
                "status": article.select_one(".status").get_text(strip=True) if article.select_one(".status") else "",
                "type": article.select_one(".typez").get_text(strip=True) if article.select_one(".typez") else "",
                "episodes": article.select_one(".epx").get_text(strip=True) if article.select_one(".epx") else "",
                "sub": article.select_one(".sb").get_text(strip=True) if article.select_one(".sb") else "",
                "url": anime_url,
                "slug": get_slug(anime_url),
                "image": img.get("src") if img else None,
            })

        pagination = scrape_pagination(soup, page)

        return jsonify({
            "source": url, "cast": cast_name, "slug": name,
            "page": page, "results": anime_list, "pagination": pagination,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
