import os
import feedparser
from datetime import datetime
import pytz

# 한국 시간 설정
KST = pytz.timezone('Asia/Seoul')
NOW = datetime.now(KST)
CURRENT_TIME_STR = NOW.strftime("%Y-%m-%d %H:%M:%S (KST)")

# 메인 대시보드 파일 (README.md로 설정하여 메인 화면에 노출)
FILE_PATH = "README.md"
RSS_URL = "https://pokemongolive.com/feeds/news.xml"

DATA_SOURCES = {
    "📢 공식 채널 (Official)": [
        {"name": "공식 트위터 (글로벌)", "url": "https://twitter.com/PokemonGoApp"},
        {"name": "공식 트위터 (한국)", "url": "https://twitter.com/PokemonGOAppKR"},
        {"name": "공식 블로그", "url": "https://pokemongolive.com/post/"},
    ],
    "⚡ 속보 및 데이터 (Intel)": [
        {"name": "LeekDuck (이벤트 일정)", "url": "https://leekduck.com/"},
        {"name": "The Silph Road", "url": "https://thesilphroad.com/"},
        {"name": "Pokémon GO Hub", "url": "https://pokemongohub.net/"},
    ],
    "📚 도감 및 DB": [
        {"name": "🇰🇷 한국 공식 도감", "url": "https://www.pokemonkorea.co.kr/pokedex"},
        {"name": "📊 GO Hub 스탯 DB", "url": "https://db.pokemongohub.net/"},
        {"name": "✨ 이로치 체크리스트", "url": "https://leekduck.com/shiny/"},
    ]
}

def fetch_latest_news():
    try:
        feed = feedparser.parse(RSS_URL)
        news_items = []
        for entry in feed.entries[:3]: 
            title = entry.title
            link = entry.link
            published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            news_items.append(f"- `[{published}]` [{title}]({link})")
        return news_items
    except:
        return ["- 뉴스 정보를 가져오지 못했습니다."]

def get_existing_history():
    """기존 파일에서 히스토리 섹션을 보존합니다."""
    if not os.path.exists(FILE_PATH):
        return ""
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if "## 🔄 업데이트 히스토리 (History)" in content:
            return content.split("## 🔄 업데이트 히스토리 (History)")[1].strip()
    except:
        pass
    return ""

def generate_dashboard():
    news_items = fetch_latest_news()
    existing_history = get_existing_history()
    
    # [화면 구성]
    md = f"# 📱 Pokémon GO Daily Ops Dashboard\n"
    md += f"**Last Updated:** {CURRENT_TIME_STR} (Python 3.12 Engine)\n\n"
    md += f"![Status](https://img.shields.io/badge/Status-Active-success) ![News](https://img.shields.io/badge/News-{len(news_items)}_Items-blue)\n\n"
    
    md += "## 🔥 오늘의 주요 소식 (Live Feed)\n"
    for item in news_items:
        md += f"{item}\n"
    md += "\n"

    md += "## 🔗 주요 정보 소스\n"
    md += "| 카테고리 | 소스 이름 | 바로가기 |\n"
    md += "| --- | --- | --- |\n"
    for category, sites in DATA_SOURCES.items():
        for site in sites:
            md += f"| {category} | **{site['name']}** | [Link]({site['url']}) |\n"
    md += "\n---\n\n"

    # 히스토리 로그 생성
    new_log = f"### ⏰ {CURRENT_TIME_STR} 리포트\n"
    new_log += f"* **시스템 상태:** 정상\n"
    new_log += f"* **수집된 뉴스:** {len(news_items)}건\n"
    new_log += "<details><summary>상세 로그 접기/펼치기</summary>\n\n"
    new_log += "Auto-generated via GitHub Actions.\n"
    new_log += "</details>\n\n"

    # 최종 컨텐츠 결합
    final_content_for_file = md + "## 🔄 업데이트 히스토리 (History)\n" + new_log + existing_history
    
    # 1. README.md 파일 저장 (리포지토리 메인 화면용)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(final_content_for_file)
        
    # 2. GitHub Actions 요약 화면 출력 (작업 결과 화면용)
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(md) # 요약 화면에는 히스토리 제외하고 최신 정보만 깔끔하게 출력
            f.write("\n\n> 🚀 **전체 히스토리는 [README](./README.md)에서 확인하세요.**")

    print("✅ Dashboard generated on README and Action Summary.")

if __name__ == "__main__":
    generate_dashboard()
