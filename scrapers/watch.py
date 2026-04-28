import os
from flask import jsonify
from .helpers import fetch_soup, get_slug, scrape_article_bs

BASE_URL = "https://samehadaku.li/"
SITE_NAME = os.getenv("SITE_NAME", "MyAnimeSite")


def watch_anime(slug):
    try:
        url = f"{BASE_URL}{slug.strip('/')}/"
        soup, _ = fetch_soup(url)

        # iframe video
        video_div = soup.select_one("div.video-content iframe")
        iframe_src = video_div.get("src") if video_div else None

        # title
        title_tag = soup.select_one("div.title-section h1.entry-title")
        title_text = title_tag.get_text(strip=True) if title_tag else ""

        # detail info block
        detail = {}
        info_box = soup.select_one("div.single-info.bixbox")
        if info_box:
            thumb = info_box.select_one(".thumb img")
            detail["thumbnail"] = thumb.get("src") if thumb else None

            series_title = info_box.select_one("h2[itemprop='partOfSeries']")
            detail["series_title"] = series_title.get_text(strip=True) if series_title else ""

            alter_title = info_box.select_one(".alter")
            detail["alter_title"] = alter_title.get_text(strip=True) if alter_title else ""

            rating = info_box.select_one(".rating strong")
            detail["rating"] = rating.get_text(strip=True) if rating else ""

            for span in info_box.select("div.spe span"):
                text = span.get_text(" ", strip=True)
                if ":" in text:
                    key, value = text.split(":", 1)
                    detail[key.strip()] = value.strip()

            casts_span = info_box.select_one("div.spe span:contains('Casts')")
            if casts_span:
                detail["casts"] = [
                    {"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")}
                    for a in casts_span.select("a")
                ]

            detail["genres"] = [
                {"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")}
                for a in info_box.select(".genxed a")
            ]

            desc = info_box.select_one(".desc.mindes")
            if desc:
                detail["description"] = desc.get_text("\n", strip=True).replace("Samehadaku", SITE_NAME)
            else:
                detail["description"] = ""

        # recommended
        recommended = []
        for article in soup.select("article.bs"):
            item = scrape_article_bs(article)
            if item:
                rec = {
                    "title_short": item["title"],
                    "title_full": item["title"],
                    "episode": item["episode"],
                    "type": item["type"],
                    "status": item["status"],
                    "url": item["url"],
                    "slug": item["slug"],
                    "image": item["image"],
                }
                recommended.append(rec)

        # episode list
        episode_list = []
        for li in soup.select("div.episodelist ul li"):
            a_tag = li.select_one("a")
            if not a_tag:
                continue
            ep_url = a_tag.get("href", "")
            img_tag = li.select_one("img")
            title = li.select_one(".playinfo h3")
            span_info = li.select_one(".playinfo span")

            episode_list.append({
                "id": li.get("data-id", ""),
                "title": title.get_text(strip=True) if title else "",
                "episode_info": span_info.get_text(strip=True) if span_info else "",
                "url": ep_url,
                "slug": get_slug(ep_url),
                "image": img_tag.get("src") if img_tag else None,
                "selected": "selected" in li.get("class", []),
            })

        return jsonify({
            "source": url,
            "slug": slug,
            "title": title_text,
            "iframe": iframe_src,
            "detail": detail,
            "episodes": episode_list,
            "recommended": recommended,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
