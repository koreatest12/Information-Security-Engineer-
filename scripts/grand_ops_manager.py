import sqlite3
import os
import datetime

DB_PATH = "data/grand_ops_secure.db"
SCHEMA_PATH = "data/schema_snapshot.sql"

def init_and_manage_db():
    print(f"🔧 Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 테이블 강제 생성 (Schema Migration)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT,
            status TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            risk_level TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 상태 점검 데이터 주입 (Health Check)
    cursor.execute("INSERT INTO service_health (service_name, status) VALUES ('Auth_Server', 'ACTIVE')")
    cursor.execute("INSERT INTO service_health (service_name, status) VALUES ('DB_Engine', 'OPTIMIZED')")
    cursor.execute("INSERT INTO access_log (action, risk_level) VALUES ('Routine Ops Check', 'SAFE')")
    
    conn.commit()
    print("✅ DB Data Injected.")
    
    # [중요] 스키마 스냅샷 생성 (git add 에러 방지용)
    with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    print(f"📄 Schema Snapshot Saved: {SCHEMA_PATH}")
    
    conn.close()

if __name__ == "__main__":
    # 폴더가 없으면 에러나므로 생성 확인
    if not os.path.exists("data"):
        os.makedirs("data")
    init_and_manage_db()
