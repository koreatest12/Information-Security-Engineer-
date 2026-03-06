import os, json, feedparser, pytz
from datetime import datetime

KST = pytz.timezone('Asia/Seoul')
NOW = datetime.now(KST)
DATE_TAG = NOW.strftime("%Y.%m.%d")

# 3월 이벤트 데이터 수동 반영 (제공해주신 정보 기반)
EVENT_INTEL = [
    {"period": "3/2~6/2", "title": "대발견: 갸라도스, 단칼빙, 타타륜, 데인차 등 ✨"},
    {"period": "3/4~3/10", "title": "전설 레이드: 프리져/파이어/썬더 ✨"},
    {"period": "3/7~3/9", "title": "포켓몬 30주년 대집합 이벤트 ⭐️"},
    {"period": "3/10~3/18", "title": "전설 레이드: 자시안 ✨ (2188/2735)"},
    {"period": "3/14", "title": "3월 커뮤니티 데이: 염버니 ✨⭐️"},
    {"period": "3/28", "title": "거다이맥스 피카츄 ✨ 맥스배틀 데이"}
]

DATA_SOURCES = {
    "📢 Official": [{"name": "Twitter (KR)", "url": "https://twitter.com/PokemonGOAppKR"}],
    "⚡ Intel": [{"name": "LeekDuck", "url": "https://leekduck.com/"}]
}

def run():
    data = {
        "timestamp": NOW.strftime("%Y-%m-%d %H:%M:%S"),
        "version": DATE_TAG,
        "events": EVENT_INTEL,
        "sources": DATA_SOURCES
    }
    os.makedirs("data", exist_ok=True)
    with open("data/daily_intel.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # README 렌더링
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# 📱 Pokémon GO Ops Center (v{DATE_TAG})\n")
        f.write(f"**Last Sync:** {data['timestamp']} (KST)\n\n")
        f.write("## 📅 핵심 이벤트 요약\n")
        for e in EVENT_INTEL:
            f.write(f"- **{e['period']}**: {e['title']}\n")

if __name__ == "__main__":
    run()
