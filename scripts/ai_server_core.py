import sqlite3
import os
import datetime
import random
import hashlib
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

# 환경 변수 및 설정
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_server.db')
DAILY_REPORT = os.getenv('DAILY_REPORT', 'data/daily_insight.md')
WEEKLY_NEWS = os.getenv('WEEKLY_NEWS', 'data/weekly_ai_news.md')

class AuditLogger:
    def __init__(self, conn):
        self.conn = conn
    
    def log(self, actor, action, details):
        try:
            raw = f"{actor}{action}{details}{datetime.datetime.now()}"
            h_val = hashlib.sha256(raw.encode()).hexdigest()
            self.conn.execute('INSERT INTO audit_trail (actor, action, details, data_hash) VALUES (?,?,?,?)', 
                              (actor, action, details, h_val))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Audit Log Error: {e}")

class DataHandler:
    def __init__(self, conn):
        self.conn = conn

    def seed_initial_data(self):
        """[Fix] 초기 데이터 부족으로 인한 에러 방지 (Seeding)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM historical_data")
        cnt = cursor.fetchone()[0]
        
        if cnt < 10:
            print("🌱 Seeding initial data for AI training...")
            data = []
            for i in range(50):
                load = np.random.normal(40, 10)
                traf = np.random.randint(500, 1500)
                lat = np.random.normal(20, 5)
                # 과거 시간으로 생성
                past_time = datetime.datetime.now() - datetime.timedelta(minutes=10*i)
                data.append((load, traf, lat, past_time))
            
            cursor.executemany('INSERT INTO historical_data (cpu_load, traffic, latency, timestamp) VALUES (?,?,?,?)', data)
            self.conn.commit()
            print("✅ Seeding Completed.")

    def collect(self):
        load = max(0, np.random.normal(50, 15))
        traffic = max(0, int(np.random.poisson(1000)))
        latency = max(0, np.random.exponential(20))
        
        self.conn.execute('INSERT INTO historical_data (cpu_load, traffic, latency) VALUES (?,?,?)', 
                          (load, traffic, latency))
        self.conn.commit()
        return load, traffic, latency

class AIEngine:
    def __init__(self, conn):
        self.conn = conn

    def analyze(self):
        # 데이터 로드
        df = pd.read_sql_query("SELECT * FROM historical_data ORDER BY timestamp DESC LIMIT 200", self.conn)
        
        # [Fix] 데이터가 부족하면 분석 스킵 (None 반환)
        if len(df) < 10:
            return None, None, df

        # 1. 이상 탐지
        try:
            iso = IsolationForest(contamination=0.05, random_state=42)
            # 학습용 데이터 (NaN 제거)
            X = df[['cpu_load', 'latency']].fillna(0)
            df['anomaly'] = iso.fit_predict(X)
            current_anomaly = df.iloc[0]['anomaly'] # 최신 데이터
        except Exception as e:
            print(f"⚠️ AI Model Error: {e}")
            current_anomaly = 1 # 기본값 정상

        # 2. 선형 예측
        try:
            reg = LinearRegression()
            # 최근 50개만 사용
            sub_df = df.head(50).iloc[::-1].reset_index(drop=True) # 시간순 정렬
            X_reg = np.array(sub_df.index).reshape(-1, 1)
            y_reg = sub_df['cpu_load'].values
            reg.fit(X_reg, y_reg)
            next_pred = reg.predict([[50]])[0]
        except Exception:
            next_pred = None

        return current_anomaly, next_pred, df

class Visualizer:
    """ASCII 차트 생성기"""
    @staticmethod
    def draw_ascii_bar(val, max_val=100):
        length = int((val / max_val) * 20)
        return "█" * length + "░" * (20 - length)

def main():
    print("🚀 AI Server Core v18.0 Starting...")
    if not os.path.exists("data"): os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    
    # 테이블 생성
    conn.execute('CREATE TABLE IF NOT EXISTS historical_data (id INTEGER PRIMARY KEY, cpu_load REAL, traffic INTEGER, latency REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS audit_trail (id INTEGER PRIMARY KEY, actor TEXT, action TEXT, details TEXT, data_hash TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    
    # 모듈 초기화
    handler = DataHandler(conn)
    engine = AIEngine(conn)
    audit = AuditLogger(conn)

    # 1. 데이터 시딩 및 수집
    handler.seed_initial_data() # [중요]
    load, traf, lat = handler.collect()
    audit.log("AI_Agent", "COLLECT", f"L:{load:.1f}, T:{traf}")

    # 2. AI 분석
    anomaly, pred, df = engine.analyze()
    
    # [Fix] 포맷팅 안전 처리
    status_str = "✅ STABLE" if anomaly == 1 else "🚨 ABNORMAL"
    pred_str = f"{pred:.2f}%" if pred is not None else "Analyzing..."
    
    # 3. 리포트 작성 (Visual ASCII Chart 포함)
    with open(DAILY_REPORT, 'w', encoding='utf-8') as f:
        f.write(f"# 📊 Grand Ops Daily Insight\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📡 System Dashboard\n")
        f.write(f"- **Current Load:** `{Visualizer.draw_ascii_bar(load)}` ({load:.1f}%)\n")
        f.write(f"- **Traffic Vol:** `{Visualizer.draw_ascii_bar(traf, 2000)}` ({traf} reqs)\n")
        f.write(f"- **Latency:** {lat:.2f} ms\n\n")
        
        f.write("## 🧠 AI Diagnosis\n")
        f.write(f"- **System Health:** {status_str}\n")
        f.write(f"- **Load Prediction (Next 10m):** {pred_str}\n")
        
        if df is not None and not df.empty:
            f.write("\n## 📉 Recent Trend (Last 5 Entries)\n")
            f.write("| Time | Load | Traffic | Status |\n|---|---|---|---|\n")
            for _, row in df.head(5).iterrows():
                ts = row.get('timestamp', 'N/A')
                ld = row['cpu_load']
                tr = row['traffic']
                st = "🔴" if row.get('anomaly', 1) == -1 else "🟢"
                f.write(f"| {ts} | {ld:.1f}% | {tr} | {st} |\n")

    print("✅ Core Logic Finished Successfully.")
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        sys.exit(1) # 에러 발생 시 명확히 알림
