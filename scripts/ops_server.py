import os
import json
import feedparser
import pytz
from datetime import datetime

# --- Configuration ---
KST = pytz.timezone('Asia/Seoul')
NOW = datetime.now(KST)
DATE_TAG = NOW.strftime("%Y.%m.%d")
CURRENT_TIME_STR = NOW.strftime("%Y-%m-%d %H:%M:%S (KST)")

RSS_URL = "https://pokemongolive.com/feeds/news.xml"
DB_FILE = "data/daily_intel.json"
README_FILE = "README.md"

DATA_SOURCES = {
    "📢 Official": [
        {"name": "Twitter (Global)", "url": "https://twitter.com/PokemonGoApp"},
        {"name": "Twitter (Korea)", "url": "https://twitter.com/PokemonGOAppKR"},
        {"name": "Blog News", "url": "https://pokemongolive.com/post/"},
    ],
    "⚡ Intel & Data": [
        {"name": "LeekDuck", "url": "https://leekduck.com/"},
        {"name": "The Silph Road", "url": "https://thesilphroad.com/"},
        {"name": "GO Hub", "url": "https://pokemongohub.net/"},
    ],
    "📚 Pokedex DB": [
        {"name": "Official Pokedex (KR)", "url": "https://www.pokemonkorea.co.kr/pokedex"},
        {"name": "GO Hub Stats", "url": "https://db.pokemongohub.net/"},
        {"name": "Shiny List", "url": "https://leekduck.com/shiny/"},
    ]
}

def collect_data():
    print("📡 [Server] Fetching external data...")
    news_data = []
    try:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries[:5]:
            published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            news_data.append({"date": published, "title": entry.title, "link": entry.link})
    except Exception as e:
        print(f"⚠️ Error: {e}")

    return {
        "timestamp": CURRENT_TIME_STR,
        "version": DATE_TAG,
        "news": news_data,
        "sources": DATA_SOURCES
    }

def save_database(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 [Server] Database saved to {DB_FILE}")

def render_dashboard(data):
    print("🎨 [Renderer] Generating Dashboard...")
    repo = os.environ.get('GITHUB_REPOSITORY', 'Grand-Ops/Pogo')
    
    md = f"# 📱 Pokémon GO Ops Center (v{data['version']})\n"
    md += f"**Server Status:** 🟢 Online | **Last Sync:** {data['timestamp']}\n\n"
    md += f"[![Release](https://img.shields.io/github/v/release/{repo}?label=Latest%20Release&color=success)](../../releases/latest) "
    md += f"![Python](https://img.shields.io/badge/Python-3.12-blue)\n\n"

    md += "## 🔥 Live Intelligence (News)\n"
    if data['news']:
        for item in data['news']:
            md += f"- `[{item['date']}]` [{item['title']}]({item['link']})\n"
    else:
        md += "- No news data available.\n"
    md += "\n"

    md += "## 🔗 Critical Links\n"
    md += "| Category | Source | Access |\n"
    md += "| --- | --- | --- |\n"
    for category, sites in data['sources'].items():
        for site in sites:
            md += f"| {category} | **{site['name']}** | [Connect]({site['url']}) |\n"
    
    md += "\n---\n"
    md += f"*Grand-Ops-Master Automated System (Engine: Python 3.12)*"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(md)
    
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"## 🚀 Ops Server Report (v{data['version']})\n")
            f.write(f"- **Data Points:** {len(data['news'])} items\n")
            f.write(f"- **Database:** `data/daily_intel.json` updated.\n")

if __name__ == "__main__":
    intel_data = collect_data()
    save_database(intel_data)
    render_dashboard(intel_data)
