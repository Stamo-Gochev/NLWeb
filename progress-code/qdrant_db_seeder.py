import json
from tqdm import tqdm
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from dotenv import load_dotenv
import os
from pathlib import Path

# ----------------------
# Environment and paths
# ----------------------
ENV_BASE_PATH = Path(__file__).resolve().parents[1]
dotenv_path = ENV_BASE_PATH / ".env"
load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env")
if QDRANT_URL is None:
    raise ValueError("QDRANT_URL not found in .env")

ROOT_PATH = Path(__file__).parent
JSONL_FILE = ROOT_PATH / "telerik-blazor-docs.jsonl"
if not JSONL_FILE.exists():
    raise FileNotFoundError(f"JSONL file not found at {JSONL_FILE}")

# ----------------------
# Config
# ----------------------
COLLECTION_NAME = os.getenv("OPENAI_API_KEY")
VECTOR_MODEL = "text-embedding-3-small"
VECTOR_SIZE = 1536
BATCH_SIZE = 100
MAX_CHARS = 24000  # truncate long text to avoid 8192 token limit

# ----------------------
# Initialize clients
# ----------------------
openai_client = OpenAI(api_key=OPENAI_API_KEY)
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, check_compatibility=False)

# ----------------------
# Create collection if it doesn't exist
# ----------------------
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=rest.VectorParams(
            size=VECTOR_SIZE,
            distance=rest.Distance.COSINE
        )
    )
else:
    print(f"Collection '{COLLECTION_NAME}' already exists — using existing collection.")

# ----------------------
# Read JSONL and prepare points
# ----------------------
points = []

with JSONL_FILE.open("r", encoding="utf-8") as f:
    for idx, line in enumerate(tqdm(f, desc="Preparing points")):
        doc = json.loads(line)

        # Get text for embedding
        text = doc.get("text") or doc.get("articleBody") or ""
        if not text.strip():
            continue

        # Truncate text to MAX_CHARS to avoid token overflow
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]

        # Compute OpenAI embedding
        response = openai_client.embeddings.create(
            model=VECTOR_MODEL,
            input=text
        )
        vector = response.data[0].embedding

        # Build payload
        payload = {
            "headline": doc.get("headline"),
            "url": doc.get("url"),
            "tags": doc.get("tags").split(","),
            "description": doc.get("description"),
            "page_title": doc.get("page_title"),
            "published": doc.get("published"),
            # "site": "https://www.telerik.com/blazor-ui/documentation"
            # "position": doc.get("position"),
        }

        # Use 'position' if exists, otherwise auto-generate
        point_id = idx

        points.append(
            rest.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        )

# ----------------------
# Batch upload to Qdrant
# ----------------------
for i in tqdm(range(0, len(points), BATCH_SIZE), desc="Uploading batches"):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points[i:i + BATCH_SIZE]
    )

print(f"Uploaded {len(points)} points to collection '{COLLECTION_NAME}'")
