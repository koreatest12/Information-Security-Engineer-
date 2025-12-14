import os
import json
import feedparser
import pytz
from datetime import datetime

# --- [Configuration] ---
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

# --- [Module 1: Collector Server] ---
def collect_data():
    """RSS 피드 및 메타 데이터를 수집하여 JSON DB 구조로 반환"""
    print("📡 [Server] Fetching external data...")
    news_data = []
    try:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries[:5]:
            published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            news_data.append({
                "date": published,
                "title": entry.title,
                "link": entry.link
            })
    except Exception as e:
        print(f"⚠️ Error fetching RSS: {e}")

    # 데이터 패킷 생성
    data_packet = {
        "timestamp": CURRENT_TIME_STR,
        "version": DATE_TAG,
        "news": news_data,
        "sources": DATA_SOURCES
    }
    return data_packet

def save_database(data):
    """수집된 데이터를 파일 시스템에 저장 (DB 역할)"""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 [Server] Data saved to {DB_FILE}")

# --- [Module 2: Dashboard Renderer] ---
def render_dashboard(data):
    """JSON 데이터를 기반으로 README.md 생성"""
    print("🎨 [Renderer] Generating Dashboard...")
    
    md = f"# 📱 Pokémon GO Ops Center (v{data['version']})\n"
    md += f"**Server Status:** 🟢 Online | **Last Sync:** {data['timestamp']}\n\n"
    
    # 뱃지 추가 (릴리즈 다운로드 링크 등)
    md += f"[![Release](https://img.shields.io/github/v/release/{os.environ.get('GITHUB_REPOSITORY', 'Grand-Ops/Pogo')}?label=Latest%20Release)](../../releases/latest) "
    md += f"![Python](https://img.shields.io/badge/Python-3.12-blue)\n\n"

    # 뉴스 섹션
    md += "## 🔥 Live Intelligence (News)\n"
    if data['news']:
        for item in data['news']:
            md += f"- `[{item['date']}]` [{item['title']}]({item['link']})\n"
    else:
        md += "- 수집된 뉴스가 없습니다.\n"
    md += "\n"

    # 링크 섹션
    md += "## 🔗 Critical Links\n"
    md += "| Category | Source | Access |\n"
    md += "| --- | --- | --- |\n"
    for category, sites in data['sources'].items():
        for site in sites:
            md += f"| {category} | {site['name']} | [Connect]({site['url']}) |\n"
    
    md += "\n---\n"
    md += f"*Grand-Ops-Master Automated System (Engine: Python 3.12)*"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(md)
    print("✅ [Renderer] README.md updated.")

    # Actions 요약 화면 출력
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"## 🚀 Ops Server Report (v{data['version']})\n")
            f.write(f"- **Data Points:** {len(data['news'])} news items collected.\n")
            f.write(f"- **Database:** [Download JSON](../../blob/main/{DB_FILE})\n")

if __name__ == "__main__":
    # 1. 데이터 수집 (Server)
    intel_data = collect_data()
    
    # 2. DB 저장 (Artifact)
    save_database(intel_data)
    
    # 3. 화면 렌더링 (View)
    render_dashboard(intel_data)
