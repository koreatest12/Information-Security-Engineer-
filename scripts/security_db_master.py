import sqlite3
import os
import hashlib
import datetime
import random
import uuid
import json
import sys

# =======================================================
# ⚙️ CONFIGURATION & DEPENDENCY CHECK
# =======================================================
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "grand_ops_archive.db")
SECURITY_MD_PATH = "SECURITY.md"

# 외부 리소스 (상태 점검용)
RESOURCE_MAP = {
    "Exam": [{"name": "CQ (정보보안기사)", "url": "https://www.cq.or.kr"}],
    "KISA": [{"name": "KISA KrCERT", "url": "https://www.boho.or.kr"}],
    "OWASP": [{"name": "OWASP Top 10", "url": "https://owasp.org"}]
}

# Requests 모듈 처리 (CI 환경 호환성)
try:
    import requests
except ImportError:
    print("⚠️ 'requests' module not found. Installing via pip...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests

# =======================================================
# 🛠️ DATABASE SCHEMA DEFINITION
# =======================================================
def init_db():
    """모든 마이크로서비스를 위한 통합 DB 스키마 생성"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. [Auth Service] 사용자 및 인증 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'USER', -- ADMIN, USER, GUEST
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. [Payment Service] 결제 트랜잭션 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id TEXT PRIMARY KEY,
            user_id TEXT,
            amount DECIMAL(10, 2),
            currency TEXT DEFAULT 'USD',
            status TEXT, -- SUCCESS, FAILED, PENDING, BLOCKED
            note TEXT,   -- 공격 시뮬레이션용 필드
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # 3. [Inventory Service] 상품 및 재고 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price REAL,
            stock_qty INTEGER,
            last_restock TIMESTAMP
        )
    ''')

    # 4. [Security HQ] 보안 정책 및 취약점 스캔 리포트
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer TEXT, asset TEXT, threat TEXT, 
            defense_logic TEXT, tool TEXT, 
            hash TEXT UNIQUE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vuln_reports (
            scan_id TEXT PRIMARY KEY,
            target_service TEXT,
            severity TEXT, -- LOW, MEDIUM, HIGH, CRITICAL
            description TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. [Admin Console] 통합 감사 로그 (Audit Logs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT,
            event_type TEXT,
            ip_address TEXT,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 6. 외부 리소스 상태
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, url TEXT, status TEXT, 
            latency_ms REAL, checked_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("✅ Database Schema & Tables Initialized Successfully.")
    return conn

# =======================================================
# 💾 MASSIVE DATA SEEDING (Simulation)
# =======================================================
def seed_massive_data(conn):
    """대량의 모의 데이터 주입 (Auth, Payment, Inventory 등)"""
    cursor = conn.cursor()
    
    # 1. Seed Users (100+ Users)
    print("   ↳ Seeding 100+ Mock Users...")
    users = []
    roles = ['USER'] * 90 + ['ADMIN'] * 5 + ['GUEST'] * 5
    for i in range(100):
        uid = str(uuid.uuid4())
        uname = f"user_{i:03d}"
        role = roles[i]
        # 취약한 비밀번호 해시 시뮬레이션
        pw_hash = hashlib.sha256(f"password{i}".encode()).hexdigest()
        users.append((uid, uname, pw_hash, role))
    
    cursor.executemany("INSERT OR IGNORE INTO users (id, username, password_hash, role) VALUES (?, ?, ?, ?)", users)

    # 2. Seed Products (50+ Items)
    print("   ↳ Seeding Inventory Data...")
    products = [
        ("Firewall License 1Y", "Software", 500.00, 100),
        ("Security Key (YubiKey)", "Hardware", 45.00, 500),
        ("VPN Subscription", "Service", 10.00, 9999),
        ("Grand Ops Sticker", "Merch", 5.00, 200)
    ]
    # 랜덤 상품 추가 생성
    for i in range(50):
        products.append((f"Legacy Module {i}", "Hardware", random.randint(10, 1000), random.randint(0, 50)))
        
    for p in products:
        cursor.execute("INSERT INTO products (name, category, price, stock_qty, last_restock) VALUES (?, ?, ?, ?, datetime('now'))", p)

    # 3. Seed Transactions (500+ Logs)
    print("   ↳ Generating 500+ Transaction Logs...")
    txs = []
    statuses = ['SUCCESS', 'SUCCESS', 'SUCCESS', 'FAILED', 'PENDING']
    
    # 일반 트랜잭션
    for _ in range(500):
        uid = random.choice(users)[0]
        txs.append((
            str(uuid.uuid4()), uid, random.uniform(10.0, 5000.0), 
            random.choice(statuses), "Purchase Item", datetime.datetime.now()
        ))
    
    # 🔴 공격 시뮬레이션 데이터: SQL Injection 시도 흔적 주입
    malicious_user = users[0][0]
    txs.append((str(uuid.uuid4()), malicious_user, 0, 'BLOCKED', "' OR '1'='1' --", datetime.datetime.now()))
    txs.append((str(uuid.uuid4()), malicious_user, 999999, 'BLOCKED', "UNION SELECT password FROM users", datetime.datetime.now()))

    cursor.executemany("INSERT OR IGNORE INTO transactions (tx_id, user_id, amount, status, note, timestamp) VALUES (?, ?, ?, ?, ?, ?)", txs)

    conn.commit()

# =======================================================
# 🔍 LOGIC PARSING & MONITORING
# =======================================================
def parse_security_md(conn):
    """SECURITY.md 파일 파싱 및 DB 적재"""
    if not os.path.exists(SECURITY_MD_PATH):
        print(f"⚠️ {SECURITY_MD_PATH} not found. Skipping MD parsing.")
        return

    print("   ↳ Parsing Security Policies from MD...")
    with open(SECURITY_MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    policies = []
    for line in lines:
        if line.strip().startswith('|') and '---' not in line and 'Layer' not in line:
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if len(cols) >= 5:
                row_hash = hashlib.sha256("".join(cols).encode()).hexdigest()
                policies.append((cols[0], cols[1], cols[2], cols[3], cols[4], row_hash))
    
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR IGNORE INTO security_logic (layer, asset, threat, defense_logic, tool, hash)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', policies)
    conn.commit()

def check_external_resources(conn):
    """외부 보안 리소스 상태 점검"""
    print("   ↳ Checking External Security Resources...")
    cursor = conn.cursor()
    for cat, items in RESOURCE_MAP.items():
        for item in items:
            try:
                start = datetime.datetime.now()
                res = requests.get(item['url'], timeout=3, headers={"User-Agent": "GrandOpsBot"})
                latency = (datetime.datetime.now() - start).total_seconds() * 1000
                status = "Active" if res.status_code == 200 else f"HTTP {res.status_code}"
            except:
                status, latency = "Down", 0.0
            
            cursor.execute('''
                INSERT INTO external_resources (name, url, status, latency_ms, checked_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (item['name'], item['url'], status, latency))
    conn.commit()

# =======================================================
# 🚀 MAIN PIPELINE EXECUTION
# =======================================================
def run_grand_ops_pipeline():
    print("\n" + "="*50)
    print("🚀 STARTING GRAND OPS DB PIPELINE (v6.0)")
    print("="*50)
    
    # 1. DB 초기화
    conn = init_db()
    
    # 2. 대량 데이터 시드 주입 (Massive Scale)
    seed_massive_data(conn)
    
    # 3. 보안 정책 파싱
    parse_security_md(conn)
    
    # 4. 외부 리소스 모니터링
    check_external_resources(conn)
    
    # 5. 요약 리포트 출력
    cursor = conn.cursor()
    print("\n📊 DATABASE STATISTICS:")
    tables = ["users", "transactions", "products", "security_logic", "external_resources"]
    for t in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"   - {t.upper().ljust(20)}: {count} records")
        
    conn.close()
    print("\n✅ Grand Ops DB Pipeline Completed Successfully.")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_grand_ops_pipeline()
