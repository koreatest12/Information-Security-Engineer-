import sqlite3
import os
import re
import requests
import datetime
import hashlib

# =======================================================
# ⚙️ CONFIGURATION & SECURITY
# =======================================================
DB_PATH = "data/security_archive.db"
SECURITY_MD_PATH = "SECURITY.md"
DB_DIR = "data"

# 리소스 목록 (이전 로직 통합)
RESOURCE_MAP = {
    "Exam": [{"name": "CQ (정보보안기사)", "url": "https://www.cq.or.kr"}],
    "KISA": [
        {"name": "KISA KrCERT", "url": "https://www.boho.or.kr"},
        {"name": "KISA Guidelines", "url": "https://www.kisa.or.kr"}
    ],
    "OWASP": [{"name": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/"}]
}

def init_db():
    """DB 초기화 및 보안 테이블 생성 (SQL Injection 방지 스키마)"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 보안 로직 테이블 (SECURITY.md 내용 저장)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer TEXT,
            asset TEXT,
            threat TEXT,
            defense_logic TEXT,
            tool TEXT,
            hash TEXT UNIQUE, -- 중복 방지용 해시
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. 외부 리소스 상태 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            url TEXT,
            status TEXT,
            latency_ms REAL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn

def parse_security_md_table():
    """SECURITY.md 파일에서 마크다운 테이블을 파싱하여 리스트로 반환"""
    data_list = []
    if not os.path.exists(SECURITY_MD_PATH):
        print(f"⚠️ {SECURITY_MD_PATH} not found.")
        return data_list

    with open(SECURITY_MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 정규식으로 테이블 행 추출 (파이프 | 로 구분된 라인)
    # 헤더와 구분선 제외
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('|') and '---' not in line and 'Layer' not in line:
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if len(cols) >= 5:
                # 데이터 무결성을 위한 해시 생성
                row_str = "".join(cols)
                row_hash = hashlib.sha256(row_str.encode()).hexdigest()
                
                data_list.append({
                    "layer": cols[0], "asset": cols[1], "threat": cols[2],
                    "defense": cols[3], "tool": cols[4], "hash": row_hash
                })
    return data_list

def check_url_security(url):
    """URL 상태 점검 및 응답 속도 측정"""
    try:
        start = datetime.datetime.now()
        res = requests.get(url, timeout=5, headers={"User-Agent": "SecurityBot/1.0"})
        duration = (datetime.datetime.now() - start).total_seconds() * 1000
        status = "Active" if res.status_code == 200 else f"Error {res.status_code}"
        return status, round(duration, 2)
    except:
        return "Down", 0.0

def run_pipeline():
    print("🚀 Starting Security DB Pipeline...")
    conn = init_db()
    cursor = conn.cursor()
    
    # --- PHASE 1: Security Logic Injection ---
    print("Phase 1: Parsing Security Logic...")
    policies = parse_security_md_table()
    for p in policies:
        # INSERT OR IGNORE: 이미 존재하는 정책(해시 기준)은 건너뜀
        cursor.execute('''
            INSERT OR IGNORE INTO security_logic (layer, asset, threat, defense_logic, tool, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (p['layer'], p['asset'], p['threat'], p['defense'], p['tool'], p['hash']))
    print(f"✅ Processed {len(policies)} security policies.")

    # --- PHASE 2: Resource Status Update ---
    print("Phase 2: Updating Resource Status...")
    # 기존 리소스 상태 기록은 남기되, 최신 상태를 추가 (Log 방식)
    for category, items in RESOURCE_MAP.items():
        for item in items:
            status, latency = check_url_security(item['url'])
            cursor.execute('''
                INSERT INTO external_resources (category, name, url, status, latency_ms, checked_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, item['name'], item['url'], status, latency, datetime.datetime.now()))
            
    # 데이터 정리 (오래된 로그 삭제 - 최근 100건만 유지 예시)
    cursor.execute('DELETE FROM external_resources WHERE id NOT IN (SELECT id FROM external_resources ORDER BY id DESC LIMIT 100)')
    
    conn.commit()
    conn.close()
    print("🎉 DB Pipeline Completed Successfully.")

if __name__ == "__main__":
    run_pipeline()
