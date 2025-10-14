import os
import glob
import json
import markdown
import re
import yaml
from pathlib import Path

# === CONFIG ===
INPUT_DIR = Path("D:/work/github/blazor-docs")
OUTPUT_FILE = "./telerik-blazor-docs.jsonl"
BASE_URL = "https://www.telerik.com/blazor-ui/documentation/"

# === HELPERS ===

def extract_front_matter(text):
    """
    Extract YAML front matter from markdown (if present).
    Returns: (metadata_dict, markdown_content)
    """
    front_matter_regex = r"^---\n(.*?)\n---\n(.*)$"
    match = re.match(front_matter_regex, text, re.DOTALL)

    if match:
        yaml_part, content = match.groups()
        try:
            metadata = yaml.safe_load(yaml_part)
        except yaml.YAMLError:
            metadata = {}
        return metadata or {}, content
    else:
        return {}, text


def markdown_to_plain_text(md_text):
    """
    Converts markdown to plain text (stripping HTML tags).
    """
    html = markdown.markdown(md_text)
    text = re.sub(r"<[^>]+>", "", html)
    text = " ".join(text.split())
    return text


def convert_markdown_file(file_path):
    """
    Reads a markdown file and converts it into a JSON-LD object.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    metadata, md_content = extract_front_matter(raw_text)

    plain_text = markdown_to_plain_text(md_content)
    html_content = markdown.markdown(md_content)
    filename = os.path.basename(file_path)
    title = metadata.get("title") or filename.replace(".md", "")
    url = f"{BASE_URL}/{metadata.get('slug', filename.replace('.md', ''))}"

    doc = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": title,
        "text": plain_text,
        "articleBody": html_content,
        "url": url,
    }

    # Include other metadata if available
    for key in ["tags", "page_title", "description", "published", "position"]:
        if key in metadata:
            doc[key] = metadata[key]

    return doc


def main():
    # md_files = glob.glob(os.path.join(INPUT_DIR, "*.md"))
    md_files = list(INPUT_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files in {INPUT_DIR}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for md_file in md_files:
            doc = convert_markdown_file(md_file)
            json_line = json.dumps(doc, ensure_ascii=False)
            out_f.write(json_line + "\n")

    print(f"✅ Wrote {len(md_files)} documents to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
