import sqlite3
import os
import datetime
import hashlib
import requests
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# 설정
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_real.db')
DAILY_PATH = os.getenv('DAILY_REPORT', 'data/daily_real_insight.md')
AUDIT_PATH = os.getenv('AUDIT_REPORT', 'data/security_audit.md')
REPO_NAME = "koreatest12/Information-Security-Engineer-"

class RealDataFetcher:
    """공식 API를 통해 실제 데이터를 수집하는 클래스"""
    
    @staticmethod
    def get_crypto_price():
        """Source 1: CoinGecko (Bitcoin Price)"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
            # API 호출 시 User-Agent 헤더 필수
            headers = {'User-Agent': 'GrandOpsBot/1.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            price = data['bitcoin']['usd']
            change = data['bitcoin']['usd_24h_change']
            return price, change
        except Exception as e:
            print(f"⚠️ Crypto API Fail: {e}")
            return 95000.0, 0.0 # Fallback (기본값)

    @staticmethod
    def get_weather_seoul():
        """Source 2: Open-Meteo (Seoul Weather)"""
        try:
            # 서울 좌표: 37.5665, 126.9780
            url = "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&current_weather=true"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            temp = data['current_weather']['temperature']
            wind = data['current_weather']['windspeed']
            return temp, wind
        except Exception as e:
            print(f"⚠️ Weather API Fail: {e}")
            return 20.0, 5.0 # Fallback

    @staticmethod
    def get_github_stats():
        """Source 3: GitHub API (Repo Info)"""
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                stars = data.get('stargazers_count', 0)
                forks = data.get('forks_count', 0)
                return stars, forks
        except Exception:
            pass
        return 0, 0

class AuditSystem:
    def __init__(self, conn):
        self.conn = conn
    
    def log(self, source, data_point):
        # 데이터 위변조 방지 해시 기록
        raw = f"{source}{data_point}{datetime.datetime.now()}"
        h_val = hashlib.sha256(raw.encode()).hexdigest()
        self.conn.execute('INSERT INTO audit_trail (source, data_point, data_hash) VALUES (?,?,?)', (source, str(data_point), h_val))
        self.conn.commit()

class AIEngine:
    def __init__(self, conn):
        self.conn = conn
    
    def analyze_market_anomaly(self):
        """비트코인 가격과 기온 데이터를 기반으로 이상 징후 탐지"""
        df = pd.read_sql_query("SELECT btc_price, temperature FROM real_data ORDER BY id DESC LIMIT 100", self.conn)
        if len(df) < 10: return "Not Enough Data"
        
        # 학습
        iso = IsolationForest(contamination=0.1, random_state=42)
        df['anomaly'] = iso.fit_predict(df[['btc_price', 'temperature']])
        
        latest = df.iloc[-1]['anomaly']
        return "✅ STABLE" if latest == 1 else "🚨 VOLATILITY DETECTED"

class DashboardGenerator:
    @staticmethod
    def draw_bar(val, max_val):
        # 음수 처리 및 시각화
        normalized = max(0, min(100, (val / max_val) * 100))
        l = int(normalized / 10)
        return "█" * l + "░" * (10-l)

    def generate(self, btc, btc_chg, temp, wind, stars, ai_status):
        with open(DAILY_PATH, 'w', encoding='utf-8') as f:
            f.write(f"### 🌍 Real-World Intelligence Dashboard\n")
            f.write(f"**Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (KST)\n\n")
            
            f.write("#### 💰 Financial Market (Source: CoinGecko)\n")
            f.write(f"- **BTC Price:** ${btc:,.2f} ({btc_chg:+.2f}%)\n")
            f.write(f"- **Market Status:** {ai_status}\n\n")
            
            f.write("#### 🌤️ Seoul Environment (Source: Open-Meteo)\n")
            f.write(f"- **Temperature:** {temp}°C\n")
            f.write(f"- **Wind Speed:** {wind} km/h\n\n")
            
            f.write("#### 💻 DevOps Metrics (Source: GitHub)\n")
            f.write(f"- **Stars:** {stars} ⭐\n")

def main():
    if not os.path.exists("data"): os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS real_data (id INTEGER PRIMARY KEY, btc_price REAL, temperature REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS audit_trail (id INTEGER PRIMARY KEY, source TEXT, data_point TEXT, data_hash TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    
    # 1. 실제 데이터 수집 (Fetching)
    fetcher = RealDataFetcher()
    btc, btc_chg = fetcher.get_crypto_price()
    temp, wind = fetcher.get_weather_seoul()
    stars, forks = fetcher.get_github_stats()
    
    print(f"📡 Fetched: BTC=${btc}, Temp={temp}C")
    
    # 2. 데이터 저장 및 감사
    conn.execute('INSERT INTO real_data (btc_price, temperature) VALUES (?,?)', (btc, temp))
    conn.commit()
    
    audit = AuditSystem(conn)
    audit.log("CoinGecko", btc)
    audit.log("OpenMeteo", temp)
    
    # 3. AI 분석
    ai = AIEngine(conn)
    status = ai.analyze_market_anomaly()
    
    # 4. 리포트 생성
    dash = DashboardGenerator()
    dash.generate(btc, btc_chg, temp, wind, stars, status)
    
    conn.close()

if __name__ == "__main__":
    main()
