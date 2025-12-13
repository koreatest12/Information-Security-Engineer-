import sqlite3
import os
import datetime
import random
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# 설정 로드
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_secure.db')
REPORT_PATH = os.getenv('REPORT_PATH', 'data/ai_threat_report.md')

class AIEngine:
    def __init__(self, conn):
        self.conn = conn
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()

    def generate_synthetic_data(self):
        """AI 학습을 위한 초기 데이터가 부족할 경우 합성 데이터 생성"""
        print("🧪 Generating synthetic training data...")
        cursor = self.conn.cursor()
        actions = ['LOGIN', 'LOGOUT', 'QUERY', 'UPDATE', 'DELETE', 'ADMIN_ACCESS']
        risks = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        # 100개의 학습용 로그 주입
        data = []
        for _ in range(100):
            act = random.choice(actions)
            risk = random.choice(risks)
            # 'DELETE'나 'CRITICAL'은 이상치로 간주될 확률을 높이기 위해 특정 패턴 부여 가능
            val = random.randint(1, 100) 
            data.append((act, risk, val))
        
        cursor.executemany("INSERT INTO security_logs (action, risk_level, execution_time_ms) VALUES (?, ?, ?)", data)
        self.conn.commit()

    def train_and_predict(self):
        """데이터를 로드하여 비정상 행위(Anomaly) 탐지"""
        print("🧠 Training AI Model (Isolation Forest)...")
        
        # Pandas로 데이터 로드
        df = pd.read_sql_query("SELECT id, action, risk_level, execution_time_ms FROM security_logs", self.conn)
        
        if len(df) < 50:
            self.generate_synthetic_data()
            df = pd.read_sql_query("SELECT id, action, risk_level, execution_time_ms FROM security_logs", self.conn)

        # Feature Engineering (문자열 -> 수치화)
        df['action_code'] = df['action'].astype('category').cat.codes
        df['risk_code'] = df['risk_level'].astype('category').cat.codes
        
        features = df[['action_code', 'risk_code', 'execution_time_ms']]
        
        # 모델 학습
        self.model.fit(features)
        
        # 예측 (-1: 이상치/공격의심, 1: 정상)
        df['anomaly_score'] = self.model.predict(features)
        df['score_val'] = self.model.decision_function(features)
        
        anomalies = df[df['anomaly_score'] == -1]
        return anomalies, len(df)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            risk_level TEXT,
            execution_time_ms INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def main():
    print("🚀 AI Copilot System v15.0 Initiated.")
    
    # 디렉토리 확인
    if not os.path.exists("data"): os.makedirs("data")
    
    conn = init_db()
    ai_engine = AIEngine(conn)
    
    # 분석 실행
    anomalies, total_count = ai_engine.train_and_predict()
    
    print(f"📊 Analysis Complete. Scanned {total_count} logs.")
    print(f"🚨 Anomalies Detected: {len(anomalies)}")
    
    # 리포트 작성
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# 🧠 AI Threat Intelligence Report\n")
        f.write(f"**Generated At:** {datetime.datetime.now()}\n\n")
        f.write("## 📊 AI Analysis Summary\n")
        f.write(f"- **Total Data Points Scanned:** {total_count}\n")
        f.write(f"- **Algorithm Used:** Isolation Forest (Unsupervised Learning)\n")
        f.write(f"- **Threats Detected:** {len(anomalies)}\n\n")
        
        if not anomalies.empty:
            f.write("## 🚨 Detected Anomalies (Potential Threats)\n")
            f.write("| ID | Action | Risk | Exec Time (ms) | Severity Score |\n")
            f.write("|---|---|---|---|---|\n")
            for _, row in anomalies.iterrows():
                f.write(f"| {row['id']} | {row['action']} | {row['risk_level']} | {row['execution_time_ms']} | {row['score_val']:.4f} |\n")
        else:
            f.write("## ✅ System Status: CLEAN\n")
            f.write("AI detected no significant anomalies in the current dataset.\n")

    conn.close()
    print("✅ AI Tasks Completed Successfully.")

if __name__ == "__main__":
    main()
