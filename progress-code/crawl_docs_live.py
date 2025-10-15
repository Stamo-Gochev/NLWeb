import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from nlweb import NLWeb
import time

# ------------------------
# CONFIGURATION
# ------------------------
START_URL = "https://www.telerik.com/blazor-ui/documentation/introduction"  # Change to the site you want to crawl
COLLECTION_NAME = "telerik_docs_live"
VECTOR_SIZE = 1536
CRAWL_LIMIT = 500  # maximum number of pages to crawl
DELAY_BETWEEN_REQUESTS = 0.5  # seconds

# ------------------------
# INITIALIZE NLWeb
# ------------------------
nlweb = NLWeb(
    db_type="qdrant",
    qdrant_config={
        "url": "https://dea9e314-6fdd-40e7-86a1-e2f62226a439.eu-central-1-0.aws.cloud.qdrant.io:6333",
        "collection_name": COLLECTION_NAME,
        "vector_size": VECTOR_SIZE
    }
)

# ------------------------
# CRAWLER SETUP
# ------------------------
visited = set()
to_visit = deque([START_URL])
domain = urlparse(START_URL).netloc

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts and styles
    for s in soup(["script", "style", "noscript"]):
        s.decompose()

    # Extract visible text
    text = soup.get_text(separator="\n")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text

# ------------------------
# MAIN CRAWL LOOP
# ------------------------
while to_visit and len(visited) < CRAWL_LIMIT:
    url = to_visit.popleft()
    if url in visited:
        continue
    visited.add(url)

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        print(f"Failed to fetch: {url}")
        continue

    text_content = extract_text_from_html(resp.text)
    if text_content:
        metadata = {"url": url, "source": "web"}
        nlweb.ingest_text(text_content, metadata=metadata)
        print(f"Ingested: {url} ({len(text_content.split())} words)")
    else:
        print(f"No text found: {url}")

    # Find internal links to crawl
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", href=True):
        link = urljoin(url, a["href"])
        link_parsed = urlparse(link)
        # Only stay on the same domain
        if link_parsed.netloc == domain and link not in visited:
            to_visit.append(link)

    time.sleep(DELAY_BETWEEN_REQUESTS)

print(f"Crawling complete. Total pages visited: {len(visited)}")
