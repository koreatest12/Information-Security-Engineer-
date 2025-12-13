import sqlite3
import os
import datetime
import hashlib
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

# 경로 설정
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_server.db')
DAILY_PATH = os.getenv('DAILY_REPORT', 'data/daily_insight.md')
WEEKLY_PATH = os.getenv('WEEKLY_REPORT', 'data/weekly_analysis.md')
AUDIT_PATH = os.getenv('AUDIT_REPORT', 'data/security_audit.md')

class AuditSystem:
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
    def __init__(self, conn):
        self.conn = conn

    def seed_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM historical_data")
        if cursor.fetchone()[0] < 10:
            print("🌱 Seeding initial data...")
            data = []
            for i in range(50):
                data.append((
                    np.random.normal(45, 12), 
                    np.random.randint(600, 1400), 
                    np.random.normal(22, 6),
                    (datetime.datetime.now() - datetime.timedelta(minutes=10*i))
                ))
            cursor.executemany('INSERT INTO historical_data (cpu_load, traffic, latency, timestamp) VALUES (?,?,?,?)', data)
            self.conn.commit()

    def collect(self):
        load = max(0, np.random.normal(50, 15))
        traffic = max(0, int(np.random.poisson(1000)))
        latency = max(0, np.random.exponential(20))
        self.conn.execute('INSERT INTO historical_data (cpu_load, traffic, latency) VALUES (?,?,?)', (load, traffic, latency))
        self.conn.commit()
        return load, traffic

class AIAnalyzer:
    def __init__(self, conn):
        self.conn = conn
    
    def analyze(self):
        df = pd.read_sql_query("SELECT * FROM historical_data ORDER BY timestamp DESC LIMIT 300", self.conn)
        if len(df) < 10: return None, None, df
        
        iso = IsolationForest(contamination=0.05, random_state=42)
        df['anomaly'] = iso.fit_predict(df[['cpu_load', 'latency']].fillna(0))
        
        reg = LinearRegression()
        sub = df.head(50).iloc[::-1].reset_index(drop=True)
        reg.fit(np.array(sub.index).reshape(-1, 1), sub['cpu_load'].values)
        pred = reg.predict([[50]])[0]
        
        return df.iloc[0]['anomaly'], pred, df

class DashboardGenerator:
    """GitHub Summary용 최적화 리포트 생성"""
    
    @staticmethod
    def draw_bar(val, max_v=100):
        # GitHub UI에서 깔끔하게 보이도록 문자 변경
        l = int((val/max_v)*15)
        return "▓" * l + "░" * (15-l)

    def generate_daily(self, load, traffic, anomaly, pred, df):
        status_icon = "🟢" if anomaly == 1 else "🔴"
        status_text = "Stable" if anomaly == 1 else "Critical"
        
        with open(DAILY_PATH, 'w', encoding='utf-8') as f:
            f.write(f"### 📡 Real-time Dashboard\n")
            f.write(f"**Status:** {status_icon} {status_text} | **Time:** {datetime.datetime.now().strftime('%H:%M:%S')}\n\n")
            
            f.write(f"| Metric | Value | Visual |\n|---|---|---|\n")
            f.write(f"| **CPU Load** | {load:.1f}% | `{self.draw_bar(load)}` |\n")
            f.write(f"| **Traffic** | {traffic} | `{self.draw_bar(traffic, 2000)}` |\n")
            f.write(f"| **AI Prediction** | {pred:.1f}% | (Next 10m) |\n\n")
            
            f.write("#### 📉 Recent Traffic Logs\n")
            f.write(df.head(5)[['timestamp', 'cpu_load', 'traffic']].to_markdown(index=False))

    def generate_weekly(self, conn):
        df = pd.read_sql_query("SELECT * FROM historical_data WHERE timestamp >= date('now', '-7 days')", conn)
        if df.empty: return
        
        with open(WEEKLY_PATH, 'w', encoding='utf-8') as f:
            f.write(f"### 📰 Weekly Intelligence\n")
            f.write(f"**Data Points:** {len(df)}\n\n")
            f.write(f"| Stat | Load | Traffic |\n|---|---|---|\n")
            f.write(f"| **Avg** | {df['cpu_load'].mean():.1f}% | {df['traffic'].mean():.0f} |\n")
            f.write(f"| **Max** | {df['cpu_load'].max():.1f}% | {df['traffic'].max()} |\n")

    def generate_audit(self, conn):
        df = pd.read_sql_query("SELECT timestamp, actor, action, details FROM audit_trail ORDER BY id DESC LIMIT 5", conn)
        if df.empty: return
        
        with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
            f.write(f"### 🛡️ Security Audit (Last 5)\n")
            f.write(df.to_markdown(index=False))

def main():
    if not os.path.exists("data"): os.makedirs("data")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS historical_data (id INTEGER PRIMARY KEY, cpu_load REAL, traffic INTEGER, latency REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS audit_trail (id INTEGER PRIMARY KEY, actor TEXT, action TEXT, details TEXT, data_hash TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    
    mgr = DataManager(conn)
    audit = AuditSystem(conn)
    ai = AIAnalyzer(conn)
    dash = DashboardGenerator()
    
    mgr.seed_data()
    load, traffic = mgr.collect()
    audit.log("System", "COLLECT", f"L:{load:.0f}")
    
    anom, pred, df = ai.analyze()
    
    # 리포트 생성
    dash.generate_daily(load, traffic, anom, pred, df)
    dash.generate_weekly(conn)
    dash.generate_audit(conn)
    
    conn.close()

if __name__ == "__main__":
    main()
