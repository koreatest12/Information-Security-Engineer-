import sqlite3
import os
import datetime
import random
import json
import pandas as pd
import numpy as np
from scipy import stats

# 설정
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_brain.db')
REPORT_PATH = os.getenv('REPORT_PATH', 'data/agi_intelligence_report.md')

class KnowledgeBrain:
    """지식 학습 및 기억 담당"""
    def __init__(self, conn):
        self.conn = conn
        
    def learn_patterns(self, df):
        """데이터로부터 통계적 지식을 추출하여 학습(저장)"""
        if df.empty: return
        
        # 학습: 실행 시간의 평균과 표준편차를 '지식'으로 저장
        avg_time = np.mean(df['execution_time'])
        std_dev = np.std(df['execution_time'])
        
        cursor = self.conn.cursor()
        # 지식 테이블에 'ExecutionTime_Baseline'이라는 개념을 업데이트
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge_base (concept, val_mean, val_std, last_learned)
            VALUES (?, ?, ?, ?)
        ''', ('EXECUTION_TIME', avg_time, std_dev, datetime.datetime.now()))
        self.conn.commit()
        return avg_time, std_dev

class LogicJudge:
    """정오 판단 및 오류 검증 담당"""
    def __init__(self, conn):
        self.conn = conn
        
    def judge_truth(self, val, concept):
        """저장된 지식(Baseline)과 비교하여 참/거짓 판단"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT val_mean, val_std FROM knowledge_base WHERE concept=?", (concept,))
        row = cursor.fetchone()
        
        if not row: return "UNKNOWN" # 지식 부족
        
        mean, std = row
        # 정오 판단 로직: 평균에서 3표준편차 이상 벗어나면 '오류(False)'로 판단
        z_score = abs((val - mean) / (std + 1e-9)) # 0나누기 방지
        
        if z_score > 3:
            return "FALSE (Error/Anomaly)"
        else:
            return "TRUE (Normal)"

class Calculator:
    """고도 계산 및 수치 해석 담당"""
    @staticmethod
    def compute_metrics(df):
        if df.empty: return {}
        
        # Numpy/Scipy를 활용한 복합 연산
        metrics = {
            "total_ops": len(df),
            "success_rate": np.mean(df['status'] == 'SUCCESS') * 100,
            "avg_exec_time": np.mean(df['execution_time']),
            "p95_exec_time": np.percentile(df['execution_time'], 95), # 95백분위수
            "variance": np.var(df['execution_time']), # 분산
            "cv": stats.variation(df['execution_time']) # 변동 계수
        }
        return metrics

def init_system():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 데이터 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ops_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT,
            status TEXT,
            execution_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 지식 저장소 (Knowledge Base) 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            concept TEXT PRIMARY KEY,
            val_mean REAL,
            val_std REAL,
            last_learned TIMESTAMP
        )
    ''')
    
    # (시뮬레이션) 데이터 생성
    ops = ['DB_SYNC', 'AUTH_CHECK', 'DATA_PROCESS']
    statuses = ['SUCCESS', 'SUCCESS', 'SUCCESS', 'FAILURE'] # 75% 성공률
    
    new_logs = []
    for _ in range(50):
        op = random.choice(ops)
        st = random.choice(statuses)
        # 정상은 10~50, 가끔 오류로 500~1000 발생
        time_val = np.random.normal(30, 5) if st == 'SUCCESS' else np.random.normal(600, 50)
        new_logs.append((op, st, time_val))
        
    cursor.executemany("INSERT INTO ops_logs (operation, status, execution_time) VALUES (?, ?, ?)", new_logs)
    conn.commit()
    return conn

def main():
    print("🧠 AGI Core Starting...")
    if not os.path.exists("data"): os.makedirs("data")
    
    conn = init_system()
    
    # 데이터 로드
    df = pd.read_sql_query("SELECT * FROM ops_logs", conn)
    
    # 1. [지능] 지식 학습 (Learning)
    brain = KnowledgeBrain(conn)
    mean, std = brain.learn_patterns(df)
    print(f"📘 Knowledge Learned: Mean={mean:.2f}, Std={std:.2f}")
    
    # 2. [계산] 고도 연산 (Calculation)
    calc = Calculator()
    metrics = calc.compute_metrics(df)
    print(f"🧮 Calculation Results: {metrics}")
    
    # 3. [판단] 정오 판단 (Judgment)
    judge = LogicJudge(conn)
    # 가장 최근 로그 하나를 가져와서 판단 테스트
    latest_val = df.iloc[-1]['execution_time']
    verdict = judge.judge_truth(latest_val, 'EXECUTION_TIME')
    print(f"⚖️ Judgment on latest value ({latest_val:.2f}): {verdict}")

    # 리포트 작성
    with open(REPORT_PATH, 'w') as f:
        f.write("# 🧠 AGI Intelligence Report\n")
        f.write(f"**Timestamp:** {datetime.datetime.now()}\n\n")
        
        f.write("## 1. 📘 Knowledge Base (Learning)\n")
        f.write(f"- **Learned Baseline Mean:** {mean:.4f} ms\n")
        f.write(f"- **Learned Baseline StdDev:** {std:.4f}\n\n")
        
        f.write("## 2. 🧮 Advanced Calculations\n")
        f.write(f"- **Success Rate:** {metrics['success_rate']:.2f}%\n")
        f.write(f"- **95th Percentile Time:** {metrics['p95_exec_time']:.2f} ms\n")
        f.write(f"- **Variance (Volatility):** {metrics['variance']:.2f}\n\n")
        
        f.write("## 3. ⚖️ Logic Judgment (Verification)\n")
        f.write(f"- **Test Value:** {latest_val:.2f}\n")
        f.write(f"- **AI Verdict:** **{verdict}**\n")
        
    conn.close()

if __name__ == "__main__":
    main()
