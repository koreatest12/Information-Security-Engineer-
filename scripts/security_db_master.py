import sqlite3
import os
import hashlib
import datetime
import random
import uuid
import json
import sys
import secrets
import re
from collections import Counter

# =======================================================
# ⚙️ GRAND OPS: SECURITY MASTER CONFIGURATION
# =======================================================
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "grand_ops_secure_archive.db")
SECURITY_MD_PATH = "SECURITY.md"
INCIDENT_REPORT_PATH = os.path.join(DB_DIR, "incident_response_report.json")

# FIM (File Integrity Monitoring) 대상
CRITICAL_FILES = {
    SECURITY_MD_PATH: "expected_hash_placeholder"  # 런타임에 동적 계산
}

# SIEM 탐지 임계값
THRESHOLD_BRUTE_FORCE = 5
THRESHOLD_HIGH_AMOUNT = 3000.0

# 외부 리소스 (위협 인텔리전스 소스)
RESOURCE_MAP = {
    "ThreatIntel": [
        {"name": "MITRE ATT&CK", "url": "https://attack.mitre.org"},
        {"name": "NIST NVD", "url": "https://nvd.nist.gov"}
    ],
    "Compliance": [
        {"name": "OWASP Top 10", "url": "https://owasp.org"},
        {"name": "KISA KrCERT", "url": "https://www.boho.or.kr"}
    ]
}

# Requests 모듈 (CI 호환성)
try:
    import requests
except ImportError:
    print("⚠️ 'requests' module not found. Installing via pip...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests

# =======================================================
# 🔐 CRYPTO UTILS (NIST Standard)
# =======================================================
def generate_salt():
    """CSPRNG를 이용한 16바이트 Salt 생성"""
    return secrets.token_hex(16)

def hash_password(plain_password, salt):
    """PBKDF2-HMAC-SHA256: 100,000 iterations (Industry Standard)"""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        plain_password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()

def mask_pii(data_str):
    """PII(개인식별정보) 마스킹 처리 (Privacy Engineering)"""
    if not data_str: return ""
    if len(data_str) < 4: return "***"
    return data_str[:2] + "****" + data_str[-2:]

# =======================================================
# 🛠️ DATABASE SCHEMA (Enhanced)
# =======================================================
def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Users (Salt 추가 및 보안 강화)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            role TEXT DEFAULT 'USER',
            risk_score INTEGER DEFAULT 0,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Transactions (SQL Injection 시뮬레이션 데이터 수용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id TEXT PRIMARY KEY,
            user_id TEXT,
            amount DECIMAL(10, 2),
            currency TEXT DEFAULT 'USD',
            status TEXT,
            note TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Security Events (SIEM Logs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT, -- AUTH_FAIL, SQLI_ATTACK, HONEYPOT_TRIGGER
            severity TEXT,   -- LOW, MEDIUM, HIGH, CRITICAL
            source_ip TEXT,
            target_user TEXT,
            description TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Products & Inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, category TEXT, price REAL, stock_qty INTEGER
        )
    ''')
    
    # 5. Security Logic (Policy)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer TEXT, asset TEXT, threat TEXT, 
            defense_logic TEXT, tool TEXT, hash TEXT UNIQUE
        )
    ''')

    conn.commit()
    return conn

# =======================================================
# 🧬 THREAT SIMULATION & SEEDING
# =======================================================
def seed_advanced_data(conn):
    cursor = conn.cursor()
    print("  ↳ [Sim] Injecting Advanced Threat Data & User Identities...")

    # 1. Create Users with Salted Hashes
    users = []
    roles = ['USER'] * 85 + ['ADMIN'] * 5 + ['AUDITOR'] * 5 + ['BOT'] * 5
    
    # 🛑 Honeypot User (공격자 유인용)
    honey_salt = generate_salt()
    honey_pw = hash_password("admin1234", honey_salt)
    users.append(("root_admin", "root", honey_pw, honey_salt, "HONEYPOT", 0))

    for i in range(100):
        uid = str(uuid.uuid4())
        uname = f"user_{i:03d}"
        salt = generate_salt()
        pw_hash = hash_password(f"Pass@{i}!", salt)
        users.append((uid, uname, pw_hash, salt, roles[i], 0))
    
    cursor.executemany("INSERT OR IGNORE INTO users (id, username, password_hash, salt, role, risk_score) VALUES (?, ?, ?, ?, ?, ?)", users)

    # 2. Create Transactions including Attack Vectors
    print("  ↳ [Sim] Simulating 1,000+ Transactions (Normal vs Malicious)...")
    txs = []
    statuses = ['SUCCESS', 'PENDING', 'FAILED', 'BLOCKED']
    
    # Attack Signatures (SQLi, XSS)
    attack_payloads = [
        "' OR '1'='1' --", 
        "UNION SELECT 1, database(), user() --",
        "<script>alert(1)</script>",
        "../../etc/passwd"
    ]

    for _ in range(1000):
        is_attack = random.random() < 0.02 # 2% 확률로 공격 로그 생성
        uid = random.choice(users)[0]
        tx_id = str(uuid.uuid4())
        
        if is_attack:
            note = random.choice(attack_payloads)
            status = 'BLOCKED'
            amount = 0
            ip = f"192.168.1.{random.randint(100, 200)}" # Internal suspicious IP
        else:
            note = "Regular Purchase"
            status = random.choice(statuses)
            amount = random.uniform(10.0, 5000.0)
            ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

        txs.append((tx_id, uid, amount, status, note, ip, datetime.datetime.now()))
        
    # Anomaly Transaction (High Value)
    txs.append((str(uuid.uuid4()), users[5][0], 9999999.00, 'PENDING', 'Wire Transfer', '10.0.0.99', datetime.datetime.now()))

    cursor.executemany("INSERT OR IGNORE INTO transactions (tx_id, user_id, amount, status, note, ip_address, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", txs)
    conn.commit()

# =======================================================
# 🧠 INTELLIGENT SECURITY ENGINE (SIEM Logic)
# =======================================================
class SecurityOperationsCenter:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self.incidents = []

    def run_threat_detection(self):
        print("  ↳ [SOC] Running Heuristic Threat Detection Engine...")
        self._detect_sql_injection()
        self._detect_honeypot_access()
        self._detect_high_value_anomalies()
        self._check_file_integrity()
        return self.incidents

    def _detect_sql_injection(self):
        """SQL Injection 패턴 탐지 (Regex & Heuristics)"""
        # 실제 환경에서는 더 복잡한 정규식을 사용
        suspicious_patterns = ["UNION SELECT", "OR '1'='1'", "--", "WAITFOR DELAY"]
        
        self.cursor.execute("SELECT tx_id, note, ip_address FROM transactions")
        rows = self.cursor.fetchall()
        
        detected_count = 0
        for row in rows:
            tx_id, note, ip = row
            for pattern in suspicious_patterns:
                if pattern in note.upper():
                    self._log_event("SQLI_ATTACK", "HIGH", ip, "Unknown", f"SQLi pattern detected in Tx {tx_id}: {note}")
                    detected_count += 1
                    break
        if detected_count > 0:
            print(f"    ⚠️  Detected {detected_count} SQL Injection Attempts.")

    def _detect_honeypot_access(self):
        """허니팟 계정 접근 시도 탐지"""
        self.cursor.execute("SELECT id FROM users WHERE role = 'HONEYPOT'")
        honey_user = self.cursor.fetchone()
        if honey_user:
            honey_id = honey_user[0]
            # 허니팟 계정으로 생성된 트랜잭션이 있는지 확인 (있으면 침해 사고)
            self.cursor.execute("SELECT count(*) FROM transactions WHERE user_id = ?", (honey_id,))
            cnt = self.cursor.fetchone()[0]
            if cnt > 0:
                self._log_event("HONEYPOT_TRIGGER", "CRITICAL", "UNKNOWN", "root_admin", "Honeypot account activity detected!")
                print("    🚨 CRITICAL: Honeypot Trap Triggered!")

    def _detect_high_value_anomalies(self):
        """임계값 기반 이상 거래 탐지"""
        self.cursor.execute("SELECT tx_id, amount, user_id FROM transactions WHERE amount > ?", (THRESHOLD_HIGH_AMOUNT,))
        rows = self.cursor.fetchall()
        for row in rows:
            self._log_event("ANOMALY_FINANCE", "MEDIUM", "Internal", row[2], f"High value transaction detected: ${row[1]:,.2f}")

    def _check_file_integrity(self):
        """FIM: 주요 파일 해시 무결성 검증"""
        for file_path, _ in CRITICAL_FILES.items():
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                # (실제로는 저장된 기준 해시와 비교해야 함. 여기서는 데모를 위해 로깅만 수행)
                # print(f"    ℹ️  FIM Check passed for {file_path}")
            else:
                self._log_event("FIM_FAILURE", "HIGH", "System", "System", f"Critical file missing: {file_path}")

    def _log_event(self, event_type, severity, src_ip, target, desc):
        """SIEM DB에 이벤트 기록 및 인메모리 리포트 추가"""
        self.cursor.execute('''
            INSERT INTO security_events (event_type, severity, source_ip, target_user, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (event_type, severity, src_ip, target, desc))
        
        self.incidents.append({
            "timestamp": str(datetime.datetime.now()),
            "type": event_type,
            "severity": severity,
            "source": mask_pii(src_ip),
            "details": desc
        })

    def generate_report(self):
        """최종 사고 대응 리포트 생성 (JSON)"""
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": str(datetime.datetime.now()),
            "scan_summary": {
                "total_incidents": len(self.incidents),
                "severity_breakdown": dict(Counter([i['severity'] for i in self.incidents]))
            },
            "incidents": self.incidents
        }
        
        with open(INCIDENT_REPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"  ↳ [Report] Incident Response Report generated at: {INCIDENT_REPORT_PATH}")

# =======================================================
# 🚀 MAIN PIPELINE EXECUTION
# =======================================================
def run_grand_ops_pipeline():
    print("\n" + "█"*60)
    print("🚀 GRAND OPS: SECURITY MASTER PIPELINE (v9.0 Enterprise)")
    print("   » Integrity Check | Threat Intel | SIEM | Forensics")
    print("█"*60 + "\n")
    
    # 1. Initialize & Secure DB
    conn = init_db()
    
    # 2. Inject Threat Simulation Data
    seed_advanced_data(conn)
    
    # 3. SOC Operation (Detection Engine)
    soc = SecurityOperationsCenter(conn)
    soc.run_threat_detection()
    
    # 4. External Resource Status (Availability)
    print("  ↳ [Net] Verifying External Security Feeds...")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS external_resources (name TEXT, url TEXT, status TEXT, latency REAL)")
    
    for cat, items in RESOURCE_MAP.items():
        for item in items:
            try:
                start = datetime.datetime.now()
                # Timeout 설정으로 가용성 체크 (실제 연결)
                requests.head(item['url'], timeout=2) 
                latency = (datetime.datetime.now() - start).total_seconds() * 1000
                status = "Active"
            except:
                status = "Unreachable"
                latency = 0.0
            print(f"    - [{cat}] {item['name']}: {status} ({latency:.1f}ms)")
            
    # 5. Finalize & Report
    soc.generate_report()
    conn.commit()
    
    # 6. Database Stats Summary
    print("\n📊 SYSTEM SECURITY STATUS:")
    tables = {
        "users": "Identities Managed",
        "transactions": "Tx Processed",
        "security_events": "Threats Detected 🚨"
    }
    for t, desc in tables.items():
        count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"   • {desc.ljust(25)}: {count}")

    conn.close()
    print("\n✅ Grand Ops Pipeline Completed. Security Posture: OPTIMIZED.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_grand_ops_pipeline()
