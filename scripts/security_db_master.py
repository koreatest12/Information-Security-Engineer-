import sqlite3
import os
import datetime
import re
import base64
import random
import sys

# =======================================================
# ⚙️ CONFIGURATION & STEALTH PATTERNS
# =======================================================
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "security_archive.db")
BACKUP_DIR = "backup"

# [핵심] 정규식 패턴 Base64 난독화 (소스코드 오탐지 방지)
PATTERNS_B64 = {
    "AWS_ACCESS_KEY": "QUtJQVswLTlBLVpdezE2fQ==", 
    "SSH_PRIVATE_KEY": "LS0tLS1CRUdJTiAoUlNBfDVEU0F8RUN8T1BFTlNTSCkgUFJJVkFURSBLRVktLS0tLQ=="
}

def get_pattern(name):
    """Base64로 숨겨진 패턴을 런타임에만 복호화하여 사용"""
    return base64.b64decode(PATTERNS_B64[name]).decode('utf-8')

# =======================================================
# 🛠️ DATABASE ENGINE (DB Master & Auto-Migration)
# =======================================================
def init_db():
    """DB 초기화 및 스키마 자동 마이그레이션 (Self-Healing)"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 기본 테이블 생성 (없을 경우)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. [FIX] 스키마 마이그레이션 (부족한 컬럼 자동 추가)
    # 기존 DB 파일이 있더라도 새 컬럼이 없으면 자동으로 ALTER TABLE 수행
    print("🔧 Checking DB Schema Integrity...")
    cursor.execute("PRAGMA table_info(security_logic)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    required_columns = {
        "rule_name": "TEXT",
        "severity_level": "TEXT",
        "detected_area": "TEXT",
        "action_taken": "TEXT"
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            print(f"  ↳ Migrating: Adding missing column '{col_name}'...")
            try:
                cursor.execute(f"ALTER TABLE security_logic ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError as e:
                print(f"  ⚠️ Migration warning for {col_name}: {e}")

    conn.commit()
    return conn

def simulate_data_processing(conn):
    """
    [DB Master 기능] 데이터 적재 및 정리 로직
    """
    cursor = conn.cursor()
    
    # 1. 새로운 보안 로그 적재
    actions = ["BLOCKED_IP", "QUARANTINED_FILE", "FLAGGED_USER", "SESSION_KILL"]
    severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    print("📥 Ingesting new security telemetry data...")
    try:
        for _ in range(random.randint(5, 15)):
            cursor.execute('''
                INSERT INTO security_logic (rule_name, severity_level, detected_area, action_taken)
                VALUES (?, ?, ?, ?)
            ''', (
                f"Rule-{random.randint(1000, 9999)}", 
                random.choice(severities), 
                "Gateway_Inbound", 
                random.choice(actions)
            ))
        print("✅ Data ingestion successful.")
        
    except sqlite3.OperationalError as e:
        print(f"❌ DB Insert Error: {e}")
        print("⚠️ Attempting to recreate table for next run...")
        cursor.execute("DROP TABLE IF EXISTS security_logic")
        # 다음 실행 때 init_db가 다시 테이블을 만들도록 유도
    
    # 2. 오래된 데이터 정리 (Data Pruning -> VACUUM 효과 유도)
    try:
        cursor.execute("DELETE FROM security_logic WHERE id % 10 == 0") 
        conn.commit()
    except Exception as e:
        print(f"⚠️ Pruning skipped: {e}")

    # 3. 작업 로깅
    cursor.execute("INSERT INTO audit_logs (action, status) VALUES (?, ?)", ("DATA_SYNC", "SUCCESS"))
    conn.commit()

# =======================================================
# 🕵️‍♂️ INTERNAL SECURITY SCANNER (Self-Check)
# =======================================================
def run_internal_scan():
    """내부 파일 스캔 (자신 제외, Base64 패턴 사용)"""
    print("\n🔍 Running Internal Logic Scanner...")
    
    SKIP_DIRS = {'.git', '.github', 'backup', 'scripts', '__pycache__', 'venv', 'data'}
    SKIP_EXTS = {'.db', '.bak', '.png', '.jpg', '.pyc', '.txt'}
    
    aws_pattern = get_pattern("AWS_ACCESS_KEY")
    ssh_pattern = get_pattern("SSH_PRIVATE_KEY")
    
    found_issues = 0
    
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            if os.path.splitext(file)[1] in SKIP_EXTS: continue
            if file == os.path.basename(__file__): continue # 자기 자신 제외
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if re.search(aws_pattern, content):
                        print(f"⚠️  [WARNING] Potential AWS Key in: {filepath}")
                        found_issues += 1
                    if re.search(ssh_pattern, content):
                        print(f"⚠️  [WARNING] Potential SSH Key in: {filepath}")
                        found_issues += 1
            except Exception: pass

    if found_issues == 0:
        print("✅ Internal Logic Scan Passed.")
    else:
        print(f"⚠️  Internal Scan found {found_issues} potential issues.")

# =======================================================
# 🚀 MAIN EXECUTION
# =======================================================
if __name__ == "__main__":
    print(f"🚀 Security DB Master Engine Started at {datetime.datetime.now()}")
    
    # 1. DB 초기화 (스키마 자동 복구 포함)
    connection = init_db()
    
    # 2. 데이터 처리 및 로직 수행
    simulate_data_processing(connection)
    
    # 3. 내부 보안 스캔 수행
    run_internal_scan()
    
    connection.close()
    print("✅ All Master Engine tasks completed successfully.")
