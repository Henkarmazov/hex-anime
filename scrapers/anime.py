import os
from flask import jsonify, request
from .helpers import fetch_soup, get_slug, scrape_article_bs, scrape_pagination

BASE_URL = "https://samehadaku.li/"
SITE_NAME = os.getenv("SITE_NAME", "MyAnimeSite")


def anime_filter():
    try:
        params = {
            "genre[]": request.args.getlist("genre[]"),
            "season[]": request.args.getlist("season[]"),
            "studio[]": request.args.getlist("studio[]"),
            "status": request.args.get("status", ""),
            "type": request.args.get("type", ""),
            "order": request.args.get("order", ""),
            "page": request.args.get("page", "1"),
        }

        soup, final_url = fetch_soup(f"{BASE_URL}anime/", params=params)

        results = []
        for article in soup.select("article.bs"):
            item = scrape_article_bs(article)
            if item:
                results.append(item)

        pagination = scrape_pagination(soup, int(params["page"]))
        # Override with hpage nav if present
        next_tag = soup.select_one(".hpage a.r")
        if next_tag:
            pagination["next_page"] = next_tag.get("href")
        prev_tag = soup.select_one(".hpage a.l")
        if prev_tag:
            pagination["prev_page"] = prev_tag.get("href")

        return jsonify({
            "source": final_url,
            "page": int(params["page"]),
            "pagination": pagination,
            "results": results,
            "count": len(results),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def anime_detail(slug):
    try:
        url = f"{BASE_URL}{slug.strip('/')}/"
        soup, _ = fetch_soup(url)

        box = soup.select_one("div.bixbox.animefull")
        if not box:
            return jsonify({"error": "Anime detail not found"}), 404

        detail = {}

        thumb = box.select_one(".thumb img")
        detail["thumbnail"] = thumb.get("src") if thumb else None

        title_tag = box.select_one(".entry-title")
        detail["title"] = title_tag.get_text(strip=True) if title_tag else ""

        alter = box.select_one(".alter")
        detail["alter_title"] = alter.get_text(strip=True) if alter else ""

        rating = box.select_one(".rating strong")
        detail["rating"] = rating.get_text(strip=True) if rating else ""

        trailer_btn = box.select_one(".trailerbutton")
        detail["trailer"] = trailer_btn.get("href") if trailer_btn else None

        for span in box.select("div.spe span"):
            text = span.get_text(" ", strip=True)
            links = span.select("a")

            if "Studio:" in text and links:
                detail["studio"] = [{"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")} for a in links]
            elif "Season:" in text and links:
                detail["season"] = [{"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")} for a in links]
            elif "Director:" in text and links:
                detail["director"] = [{"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")} for a in links]
            elif "Producers:" in text and links:
                detail["producers"] = [{"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")} for a in links]
            elif ":" in text:
                key, value = text.split(":", 1)
                detail[key.strip().lower().replace(" ", "_")] = value.strip()
            elif span.find("time"):
                key = text.split(":")[0].strip().lower().replace(" ", "_")
                detail[key] = span.find("time").get_text(strip=True)

        detail["genres"] = [
            {"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")}
            for a in box.select(".genxed a")
        ]

        desc = box.select_one(".desc")
        detail["description"] = desc.get_text("\n", strip=True).replace("Samehadaku", SITE_NAME) if desc else ""

        synp_box = soup.select_one("div.bixbox.synp .entry-content")
        detail["synopsis"] = "\n".join(
            p.get_text(" ", strip=True) for p in synp_box.find_all("p")
        ) if synp_box else ""

        # Characters & Voice Actors
        characters = []
        char_box = soup.select_one("div.bixbox.charvoice .cvlist")
        if char_box:
            for item in char_box.select(".cvitem"):
                char_data, actor_data = {}, {}
                char = item.select_one(".cvsubitem.cvchar")
                if char:
                    img = char.select_one("img")
                    char_data = {
                        "name": char.select_one(".charname").get_text(strip=True) if char.select_one(".charname") else "",
                        "role": char.select_one(".charrole").get_text(strip=True) if char.select_one(".charrole") else "",
                        "image": img["src"] if img else None,
                    }
                actor = item.select_one(".cvsubitem.cvactor")
                if actor:
                    a_tag = actor.select_one("a")
                    img = actor.select_one("img")
                    actor_data = {
                        "name": actor.select_one(".charname").get_text(strip=True) if actor.select_one(".charname") else "",
                        "role": actor.select_one(".charrole").get_text(strip=True) if actor.select_one(".charrole") else "",
                        "image": img["src"] if img else None,
                        "link": a_tag["href"] if a_tag else None,
                        "slug": get_slug(a_tag["href"]) if a_tag else None,
                    }
                if char_data or actor_data:
                    characters.append({"character": char_data, "voice_actor": actor_data})
        detail["characters_voice_actors"] = characters

        detail["tags"] = [
            {"name": a.get_text(strip=True), "slug": get_slug(a.get("href")), "link": a.get("href")}
            for a in box.select(".bottom.tags a")
        ]

        # Episode list
        episode_list = []
        for li in soup.select("div.eplister ul li"):
            a_tag = li.select_one("a")
            if not a_tag:
                continue
            ep_url = a_tag.get("href", "")
            episode_list.append({
                "episode": li.select_one(".epl-num").get_text(strip=True) if li.select_one(".epl-num") else "",
                "title": li.select_one(".epl-title").get_text(strip=True) if li.select_one(".epl-title") else "",
                "sub": li.select_one(".epl-sub").get_text(strip=True) if li.select_one(".epl-sub") else "",
                "date": li.select_one(".epl-date").get_text(strip=True) if li.select_one(".epl-date") else "",
                "url": ep_url,
                "slug": get_slug(ep_url),
            })

        recommended_series = []
        for article in soup.select("div.bixbox .listupd article.bs"):
            item = scrape_article_bs(article)
            if item:
                recommended_series.append(item)

        return jsonify({
            "source": url,
            "slug": slug,
            "detail": detail,
            "episodes": episode_list,
            "recommended_series": recommended_series,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
