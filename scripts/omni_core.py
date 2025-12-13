import sqlite3
import os
import datetime
import requests
import psutil
import feedparser
import shutil
import tarfile
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.ensemble import IsolationForest

# 설정
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_universe.db')
DASH_PATH = os.getenv('DASHBOARD_FILE', 'data/omni_dashboard.md')
RELEASE_DIR = os.getenv('RELEASE_DIR', 'dist')

class NewsEngine:
    """📰 전 세계 뉴스 수집 및 AI 감정 분석"""
    def __init__(self):
        self.feeds = {
            "🛡️ Cyber Security": [
                "https://feeds.feedburner.com/TheHackersNews",
                "https://krebsonsecurity.com/feed/",
                "https://www.darkreading.com/rss.xml"
            ],
            "🤖 AI & Tech": [
                "https://techcrunch.com/category/artificial-intelligence/feed/",
                "https://www.wired.com/feed/category/science/latest/rss"
            ],
            "🌍 World & Politics": [
                "http://feeds.bbci.co.uk/news/world/rss.xml",
                "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            ],
            "💰 Business & Economy": [
                "https://www.cnbc.com/id/10000664/device/rss/rss.html"
            ],
            "🎬 Entertainment & Culture": [
                "https://www.variety.com/rss",
            ]
        }
        self.all_headlines = []

    def fetch_and_analyze(self):
        news_board = {}
        total_sentiment = 0
        count = 0
        
        for category, urls in self.feeds.items():
            items = []
            for url in urls:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:2]: # 소스당 2개씩만
                        title = entry.title
                        link = entry.link
                        # AI 감정 분석
                        blob = TextBlob(title)
                        sentiment = blob.sentiment.polarity # -1.0 ~ 1.0
                        total_sentiment += sentiment
                        count += 1
                        self.all_headlines.append(title)
                        
                        # 감정 아이콘
                        s_icon = "😐"
                        if sentiment > 0.1: s_icon = "🙂"
                        elif sentiment < -0.1: s_icon = "😨"
                        
                        items.append(f"{s_icon} [{title}]({link})")
                except: pass
            news_board[category] = items
        
        avg_sentiment = total_sentiment / count if count > 0 else 0
        return news_board, avg_sentiment

class HistoryVisualizer:
    """📈 데이터 누적 및 시각화 (ASCII Chart)"""
    def __init__(self, conn):
        self.conn = conn

    def draw_sparkline(self, data_list):
        if not data_list: return "No Data"
        # 간단한 스파크라인 생성 (높낮이 표현)
        min_v = min(data_list)
        max_v = max(data_list)
        span = max_v - min_v if max_v != min_v else 1
        
        chars = "  ▂▃▄▅▆▇█"
        spark = ""
        for val in data_list:
            idx = int((val - min_v) / span * 8)
            spark += chars[idx]
        return spark

    def get_trends(self):
        # 최근 20개 데이터 조회 (누적 데이터 활용)
        df = pd.read_sql_query("SELECT cpu_usage, btc_price FROM system_logs ORDER BY id DESC LIMIT 20", self.conn)
        if df.empty: return "N/A", "N/A"
        
        # 시간 역순이므로 뒤집기
        cpu_trend = self.draw_sparkline(df['cpu_usage'].iloc[::-1].tolist())
        btc_trend = self.draw_sparkline(df['btc_price'].iloc[::-1].tolist())
        return cpu_trend, btc_trend

class SystemMonitor:
    @staticmethod
    def get_stats():
        return psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage('/').percent
        
class ExternalFetcher:
    @staticmethod
    def get_bitcoin():
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", headers={'User-Agent': 'Bot'}, timeout=3)
            return r.json()['bitcoin']['usd']
        except: return 0.0

class DashboardGenerator:
    def generate(self, sys_stats, btc, trends, news_data, sentiment, ver):
        cpu, ram, disk = sys_stats
        cpu_chart, btc_chart = trends
        
        # 감정 상태 해석
        sent_str = "Neutral 😐"
        if sentiment > 0.1: sent_str = "Positive 🟢 (Hopeful News)"
        elif sentiment < -0.1: sent_str = "Negative 🔴 (Risky News)"
        
        with open(DASH_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# 🌌 Grand Ops Omni-Universe Dashboard\n")
            f.write(f"> **Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Version:** `{ver}`\n\n")

            # 1. AI & 데이터 인사이트 (누적 데이터)
            f.write("### 🧠 AI & Data Insights (Accumulated History)\n")
            f.write(f"| Metric | Current | Trend (Past 10h) | AI Analysis |\n|---|---|---|---|\n")
            f.write(f"| **CPU Load** | {cpu}% | `{cpu_chart}` | Auto-Scaling Check |\n")
            f.write(f"| **BTC Price** | ${btc:,.2f} | `{btc_chart}` | Market Volatility |\n")
            f.write(f"| **Global Mood** | {sentiment:.2f} | **{sent_str}** | Based on {sum(len(v) for v in news_data.values())} Articles |\n\n")

            # 2. 시스템 상태
            f.write("### 🖥️ System Status\n")
            f.write(f"- **RAM:** {ram}% Used\n- **Disk:** {disk}% Used\n\n")

            # 3. 글로벌 뉴스룸 (대분류)
            f.write("### 📰 Global News Omni-Channel\n")
            for cat, items in news_data.items():
                f.write(f"#### {cat}\n")
                for item in items:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            f.write("---\n*Generated by Grand Ops Omni-Universe v25.0*")

def main():
    if not os.path.exists("data"): os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS system_logs (id INTEGER PRIMARY KEY, cpu_usage REAL, btc_price REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    
    # 1. 데이터 수집
    sys = SystemMonitor.get_stats()
    ext_btc = ExternalFetcher.get_bitcoin()
    
    # DB 누적 (Accumulation)
    conn.execute("INSERT INTO system_logs (cpu_usage, btc_price) VALUES (?, ?)", (sys[0], ext_btc))
    conn.commit()
    
    # 2. 뉴스 및 AI 감정 분석
    print("📡 Analyzing Global News Sentiments...")
    news_engine = NewsEngine()
    news_data, sentiment_score = news_engine.fetch_and_analyze()
    
    # 3. 누적 데이터 시각화 (History)
    viz = HistoryVisualizer(conn)
    trends = viz.get_trends()
    
    # 4. 패키징 (버전 생성)
    ver = datetime.datetime.now().strftime("v%Y.%m.%d")
    
    # 5. 대시보드 생성
    dash = DashboardGenerator()
    dash.generate(sys, ext_btc, trends, news_data, sentiment_score, ver)
    
    conn.close()
    print("✅ Omni-Universe Cycle Completed.")

if __name__ == "__main__":
    main()
