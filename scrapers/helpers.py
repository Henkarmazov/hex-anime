import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AnimeScraper/1.0)"}


def fetch_soup(url: str, params: dict = None) -> tuple[BeautifulSoup, str]:
    """Fetch a URL and return (BeautifulSoup, final_url)."""
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    return BeautifulSoup(r.text, "html.parser"), r.url


def get_slug(url: str) -> str:
    try:
        return requests.utils.urlparse(url).path.strip("/")
    except Exception:
        return url


def scrape_article_bs(article) -> dict:
    """Parse a standard article.bs card into a dict."""
    a_tag = article.select_one("a")
    if not a_tag:
        return None

    url = a_tag.get("href", "")
    slug = get_slug(url)

    title = article.select_one(".tt") or article.select_one("h2")
    episode = article.select_one(".epx")
    status = article.select_one(".sb")
    anime_type = article.select_one(".typez")
    image = article.select_one("img")

    return {
        "title": title.get_text(strip=True) if title else "",
        "episode": episode.get_text(strip=True) if episode else "",
        "status": status.get_text(strip=True) if status else "",
        "type": anime_type.get_text(strip=True) if anime_type else "",
        "url": url,
        "slug": slug,
        "image": image.get("src") if image else None,
    }


def scrape_pagination(soup, current_page: int) -> dict:
    """Extract pagination info from soup."""
    pagination = {
        "current_page": current_page,
        "total_pages": None,
        "next_page": None,
        "prev_page": None,
    }

    page_links = soup.select(".pagination a.page-numbers")
    if page_links:
        try:
            pagination["total_pages"] = int(page_links[-1].get_text(strip=True))
        except (ValueError, AttributeError):
            pass

    prev_link = soup.select_one(".pagination a.prev")
    if prev_link:
        pagination["prev_page"] = prev_link.get("href")

    next_link = soup.select_one(".pagination a.next")
    if next_link:
        pagination["next_page"] = next_link.get("href")

    return pagination
