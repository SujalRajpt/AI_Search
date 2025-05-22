import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json


def scrape_tool_info(url):
    """
    Scrapes basic tool information from the given URL.
    Returns a dictionary with title, description, tags, and website info.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to get description from meta tag
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            description = desc_tag["content"]
        else:
            # Fallback: use the first <p> tag
            p = soup.find("p")
            description = p.text.strip() if p else ""

        # Get title from <title> tag
        title = soup.title.string.strip() if soup.title else url

        # Get tags from meta keywords
        tags = []
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            tags = [kw.strip() for kw in keywords_tag["content"].split(",")]

        return {
            "id": url.split("//")[-1].split("/")[0].replace(".", "_"),
            "title": title,
            "description": description,
            "tags": tags,
            "website": url,
        }

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return None


# === Load input CSV ===
df = pd.read_csv("ai_tools_input_with_websites.csv")

results = []
failed_urls = []

# === Scrape each URL ===
for idx, row in df.iterrows():
    url = row["website"]
    print(f"🔍 Scraping ({idx + 1}/{len(df)}): {url}")

    data = scrape_tool_info(url)

    if data:
        results.append(data)
    else:
        failed_urls.append(url)

    # Respectful delay between requests
    time.sleep(1)

# === Save outputs ===
with open("ai_tools_db.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

with open("failed_urls.txt", "w") as f:
    f.write("\n".join(failed_urls))

print(f"\n✅ Done! {len(results)} tools saved | ❌ {len(failed_urls)} failed.")
