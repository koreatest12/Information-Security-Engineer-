import os
import feedparser
from datetime import datetime
import pytz
import re

# 한국 시간 설정
KST = pytz.timezone('Asia/Seoul')
NOW = datetime.now(KST)
CURRENT_TIME_STR = NOW.strftime("%Y-%m-%d %H:%M:%S (KST)")
DATE_TAG = NOW.strftime("%Y-%m-%d")

# 파일 경로
FILE_PATH = "POGO_DAILY_BRIEF.md"
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
        for entry in feed.entries[:3]: # 최신 3개만 요약
            title = entry.title
            link = entry.link
            published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            news_items.append(f"- `[{published}]` [{title}]({link})")
        return news_items
    except:
        return ["- 뉴스 정보를 가져오지 못했습니다."]

def get_existing_history():
    """기존 파일에서 '🔄 업데이트 히스토리' 섹션 아래의 내용을 추출합니다."""
    if not os.path.exists(FILE_PATH):
        return ""
    
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 히스토리 섹션이 있는지 확인
    if "## 🔄 업데이트 히스토리 (History)" in content:
        # 히스토리 뒷부분만 잘라냄
        return content.split("## 🔄 업데이트 히스토리 (History)")[1].strip()
    return ""

def generate_dashboard():
    news_items = fetch_latest_news()
    existing_history = get_existing_history()
    
    # 1. 상단: 최신 상태 (매번 갱신)
    md = f"# 📱 Pokémon GO Daily Ops Dashboard\n"
    md += f"**Last Updated:** {CURRENT_TIME_STR} (Engine: Python 3.12)\n\n"
    md += "> Grand-Ops-Master님을 위한 실시간 브리핑 대시보드입니다.\n\n"

    # 2. 실시간 뉴스 섹션
    md += "## 🔥 오늘의 주요 소식 (Live Feed)\n"
    for item in news_items:
        md += f"{item}\n"
    md += "\n"

    # 3. 링크 모음
    md += "## 🔗 주요 정보 소스\n"
    md += "| 카테고리 | 소스 이름 | 바로가기 |\n"
    md += "| --- | --- | --- |\n"
    for category, sites in DATA_SOURCES.items():
        for site in sites:
            md += f"| {category} | **{site['name']}** | [Link]({site['url']}) |\n"
    md += "\n---\n\n"

    # 4. 하단: 히스토리 누적 (새로운 로그 + 과거 로그)
    md += "## 🔄 업데이트 히스토리 (History)\n"
    
    # 이번 실행에 대한 로그 생성
    new_log = f"### ⏰ {CURRENT_TIME_STR} 리포트\n"
    new_log += f"* **시스템 상태:** 정상\n"
    new_log += f"* **수집된 뉴스:** {len(news_items)}건\n"
    new_log += "<details><summary>상세 로그 보기</summary>\n\n"
    new_log += "Auto-generated via GitHub Actions.\n"
    new_log += "</details>\n\n"

    # 최종 결합: 상단내용 + 헤더 + (최신로그 + 과거로그)
    final_content = md + new_log + existing_history
    
    return final_content

if __name__ == "__main__":
    report = generate_dashboard()
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ Dashboard updated with cumulative history.")
