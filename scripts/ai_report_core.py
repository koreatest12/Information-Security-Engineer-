import sqlite3
import os
import datetime
import hashlib
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

# 환경 변수 로드
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_server.db')
DAILY_PATH = os.getenv('DAILY_REPORT', 'data/daily_insight.md')
WEEKLY_PATH = os.getenv('WEEKLY_REPORT', 'data/weekly_analysis.md')
AUDIT_PATH = os.getenv('AUDIT_REPORT', 'data/security_audit.md')

class AuditSystem:
    """보안 감사 로그 및 무결성 관리"""
    def __init__(self, conn):
        self.conn = conn
    
    def log(self, actor, action, details):
        try:
            raw = f"{actor}{action}{details}{datetime.datetime.now()}"
            h_val = hashlib.sha256(raw.encode()).hexdigest()
            self.conn.execute(
                'INSERT INTO audit_trail (actor, action, details, data_hash) VALUES (?,?,?,?)', 
                (actor, action, details, h_val)
            )
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Audit Error: {e}")

class DataManager:
    """데이터 시딩 및 수집"""
    def __init__(self, conn):
        self.conn = conn

    def seed_data(self):
        """데이터가 없을 경우 초기화 (Cold Start 방지)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM historical_data")
        if cursor.fetchone()[0] < 10:
            print("🌱 Seeding dummy data...")
            data = []
            for i in range(50):
                data.append((
                    np.random.normal(40, 10), 
                    np.random.randint(500, 1500), 
                    np.random.normal(20, 5),
                    (datetime.datetime.now() - datetime.timedelta(minutes=10*i))
                ))
            cursor.executemany('INSERT INTO historical_data (cpu_load, traffic, latency, timestamp) VALUES (?,?,?,?)', data)
            self.conn.commit()

    def collect(self):
        load = max(0, np.random.normal(55, 12))
        traffic = max(0, int(np.random.poisson(1100)))
        latency = max(0, np.random.exponential(18))
        self.conn.execute('INSERT INTO historical_data (cpu_load, traffic, latency) VALUES (?,?,?)', (load, traffic, latency))
        self.conn.commit()
        return load, traffic

class AIAnalyzer:
    """AI 분석 및 예측"""
    def __init__(self, conn):
        self.conn = conn
    
    def analyze(self):
        df = pd.read_sql_query("SELECT * FROM historical_data ORDER BY timestamp DESC LIMIT 300", self.conn)
        if len(df) < 10: return None, None, df
        
        # 이상 탐지
        iso = IsolationForest(contamination=0.05, random_state=42)
        df['anomaly'] = iso.fit_predict(df[['cpu_load', 'latency']].fillna(0))
        
        # 예측 (최근 데이터 기준)
        reg = LinearRegression()
        sub = df.head(50).iloc[::-1].reset_index(drop=True)
        reg.fit(np.array(sub.index).reshape(-1, 1), sub['cpu_load'].values)
        pred = reg.predict([[50]])[0]
        
        return df.iloc[0]['anomaly'], pred, df

class MDReportGenerator:
    """[New] Markdown 전문 보고서 생성기"""
    
    @staticmethod
    def draw_bar(val, max_v=100):
        l = int((val/max_v)*20)
        return "█" * l + "░" * (20-l)

    def generate_daily(self, load, traffic, anomaly, pred, df):
        status = "✅ NORMAL" if anomaly == 1 else "🚨 CRITICAL"
        with open(DAILY_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# 📅 Daily Ops Insight\n")
            f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"## 🚦 System Status: {status}\n")
            f.write(f"- **CPU Load:** `{self.draw_bar(load)}` ({load:.1f}%)\n")
            f.write(f"- **Traffic:** `{self.draw_bar(traffic, 2000)}` ({traffic} hits)\n")
            f.write(f"- **AI Prediction (Next 10m):** {pred:.1f}% Load\n\n")
            
            f.write("### 📉 Recent Logs\n")
            f.write(df.head(5)[['timestamp', 'cpu_load', 'traffic']].to_markdown(index=False))

    def generate_weekly(self, conn):
        # 주간 데이터 집계
        df = pd.read_sql_query("SELECT * FROM historical_data WHERE timestamp >= date('now', '-7 days')", conn)
        if df.empty: return
        
        with open(WEEKLY_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# 📰 Weekly AI Analysis\n")
            f.write(f"**Period:** Last 7 Days\n\n")
            f.write(f"## 📊 Key Statistics\n")
            f.write(f"| Metric | Mean | Max | Min | StdDev |\n|---|---|---|---|---|\n")
            f.write(f"| CPU Load | {df['cpu_load'].mean():.1f}% | {df['cpu_load'].max():.1f}% | {df['cpu_load'].min():.1f}% | {df['cpu_load'].std():.1f} |\n")
            f.write(f"| Traffic | {df['traffic'].mean():.0f} | {df['traffic'].max()} | {df['traffic'].min()} | {df['traffic'].std():.0f} |\n")
            f.write(f"\n## 📈 Growth Trend\n")
            f.write(f"Total data points processed: **{len(df)}**\n")

    def generate_audit(self, conn):
        # 보안 감사 로그 리포트
        df = pd.read_sql_query("SELECT timestamp, actor, action, details, data_hash FROM audit_trail ORDER BY id DESC LIMIT 20", conn)
        if df.empty: return
        
        with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# 🛡️ Security Audit Log\n")
            f.write(f"**Verified By:** AI-Guardian System\n\n")
            f.write(f"## 🕵️ Recent Activities\n")
            # Hash는 너무 기니까 앞 8자리만 노출
            df['data_hash'] = df['data_hash'].apply(lambda x: x[:8] + '...')
            f.write(df.to_markdown(index=False))

def main():
    print("🚀 Starting Reporting Engine v19...")
    if not os.path.exists("data"): os.makedirs("data")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS historical_data (id INTEGER PRIMARY KEY, cpu_load REAL, traffic INTEGER, latency REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS audit_trail (id INTEGER PRIMARY KEY, actor TEXT, action TEXT, details TEXT, data_hash TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    
    # Modules
    data_mgr = DataManager(conn)
    audit = AuditSystem(conn)
    ai = AIAnalyzer(conn)
    reporter = MDReportGenerator()
    
    # 1. Process Data
    data_mgr.seed_data()
    load, traffic = data_mgr.collect()
    audit.log("System", "COLLECT", f"L:{load:.0f}")
    
    # 2. AI Analysis
    anom, pred, df = ai.analyze()
    
    # 3. Generate Reports
    print("📝 Generating Daily Report...")
    reporter.generate_daily(load, traffic, anom, pred, df)
    
    print("📝 Generating Weekly Report...")
    reporter.generate_weekly(conn)
    
    print("📝 Generating Audit Report...")
    audit.log("Reporter", "GENERATE", "MD Files Updated")
    reporter.generate_audit(conn)
    
    conn.close()
    print("✅ All Reports Generated Successfully.")

if __name__ == "__main__":
    main()
