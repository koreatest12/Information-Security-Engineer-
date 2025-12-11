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
INCIDENT_REPORT_PATH = os.path.join(DB_DIR, "incident_response_report.json")
SENSITIVE_DOC_PATH = "./메인보고서.md"  # 사용자가 지정한 타겟 파일

# 🚨 DLP (Secret Scanning) 패턴 정의 (Regex)
# 실제 상용 도구(Gitleaks 등)에서 사용하는 패턴의 간소화 버전
DLP_PATTERNS = {
    "SSH_PRIVATE_KEY": r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
    "AWS_ACCESS_KEY": r"AKIA[0-9A-Z]{16}",
    "GENERIC_SECRET": r"(?i)(api_key|secret|password|token)\s*[:=]\s*['\"][a-zA-Z0-9@#$%^&+=]{8,}['\"]",
    "ENV_VAR_LEAK": r"(?i)(STAGING|PRODUCTION)_KEY"
}

# SIEM 탐지 임계값
THRESHOLD_BRUTE_FORCE = 5
THRESHOLD_HIGH_AMOUNT = 3000.0

# 외부 리소스
RESOURCE_MAP = {
    "ThreatIntel": [{"name": "MITRE ATT&CK", "url": "https://attack.mitre.org"}],
    "Compliance": [{"name": "KISA KrCERT", "url": "https://www.boho.or.kr"}]
}

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests")
    import requests

# =======================================================
# 🔐 CRYPTO & UTILS
# =======================================================
def generate_salt():
    return secrets.token_hex(16)

def hash_password(plain_password, salt):
    return hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000).hex()

def mask_pii(data_str):
    if not data_str: return ""
    if len(data_str) < 4: return "***"
    return data_str[:2] + "****" + data_str[-2:]

# =======================================================
# 🛠️ DATABASE SCHEMA
# =======================================================
def init_db():
    if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users, Transactions, Products, Policies
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, salt TEXT, role TEXT, risk_score INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (tx_id TEXT PRIMARY KEY, user_id TEXT, amount DECIMAL, status TEXT, note TEXT, ip_address TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Security Events (SIEM Logs) - 소스코드 스캔 결과도 여기에 저장됨
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT, -- DLP_LEAK, SQLI_ATTACK, etc.
            severity TEXT,   -- CRITICAL, HIGH, MEDIUM, LOW
            source TEXT,     -- File path or IP address
            description TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

# =======================================================
# 🕵️‍♂️ DLP & SECRET SCANNER (NEW FEATURE)
# =======================================================
class SecretScanner:
    def __init__(self, conn):
        self.conn = conn
        self.found_secrets = []

    def seed_leaked_file(self):
        """[Simulation] Secret이 유출된 '메인보고서.md' 파일 생성"""
        print(f"  ↳ [DLP] Generatig sensitive file for simulation: {SENSITIVE_DOC_PATH}")
        content = """
# 프로젝트 메인 보고서
## 1. 인프라 접속 정보 (절대 외부 유출 금지)

아래 키는 개발팀 내부 공유용입니다.
- Staging Server:
SSH_PRIVATE_KEY_STAGING = "-----BEGIN RSA PRIVATE KEY-----MIIEowIBAAKCAQEA..."

- Production DB:
SSH_PRIVATE_KEY_PRODUCTION = "-----BEGIN RSA PRIVATE KEY-----MIIEpQIBAAKCAQEA..."

- Legacy System:
SSH_PRIVATE_KEY = "SECRET_KEY_12345"
        """
        with open(SENSITIVE_DOC_PATH, "w", encoding="utf-8") as f:
            f.write(content)

    def scan_workspace(self):
        """작업 디렉토리를 스캔하여 패턴 매칭 수행"""
        print("\n🔍 Starting Pre-flight Security Scan (DLP)...")
        
        target_files = [SENSITIVE_DOC_PATH] # 실제로는 glob.glob("**/*") 등을 사용
        leak_detected = False

        for file_path in target_files:
            if not os.path.exists(file_path): continue
            
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line_idx, line in enumerate(lines):
                for leak_type, pattern in DLP_PATTERNS.items():
                    if re.search(pattern, line):
                        leak_detected = True
                        clean_line = line.strip()[:40] + "..." # 로그에는 일부만 노출
                        
                        # 1. Console Output (사용자 요청 포맷 준수)
                        print(f"{file_path}:{leak_type}    # Line {line_idx+1}: {clean_line}")
                        
                        # 2. Log to SIEM DB
                        self.conn.execute('''
                            INSERT INTO security_events (event_type, severity, source, description)
                            VALUES (?, ?, ?, ?)
                        ''', ("SECRET_LEAK", "CRITICAL", file_path, f"Found {leak_type} at line {line_idx+1}"))

        if leak_detected:
            print("❌ CRITICAL: Potential secret found in source code!")
            self.found_secrets.append("Secrets Detected")
            # 실제 CI/CD였다면 여기서 sys.exit(1)을 호출하지만, 
            # 파이프라인 진행을 보여주기 위해 에러 메시지만 출력하고 계속 진행합니다.
            print("⚠️  Blocking pipeline execution simulated... (Continuing for demo)")
        else:
            print("✅ No secrets found.")

# =======================================================
# 🧬 THREAT SIMULATION & SOC LOGIC
# =======================================================
def seed_data(conn):
    cursor = conn.cursor()
    # Mock Users & Transactions (간소화)
    if cursor.execute("SELECT count(*) FROM users").fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (id, username, role) VALUES (?, ?, ?)", (str(uuid.uuid4()), "admin", "ADMIN"))
        cursor.execute("INSERT INTO transactions (tx_id, user_id, amount, note) VALUES (?, ?, ?, ?)", 
                       (str(uuid.uuid4()), "admin", 0, "' OR '1'='1' --")) # SQL Injection Log
    conn.commit()

class SecurityOperationsCenter:
    def __init__(self, conn):
        self.conn = conn
        self.incidents = []

    def run_detection(self):
        print("  ↳ [SOC] analyzing logs...")
        cursor = self.conn.cursor()
        
        # SQL Injection Detection
        cursor.execute("SELECT tx_id, note FROM transactions WHERE note LIKE '%OR%1=1%'")
        for row in cursor.fetchall():
            self._log_incident("SQLI_ATTACK", "HIGH", "DB_LOG", f"SQL Injection pattern in tx {row[0]}")

    def _log_incident(self, event_type, severity, source, desc):
        self.conn.execute("INSERT INTO security_events (event_type, severity, source, description) VALUES (?, ?, ?, ?)", 
                          (event_type, severity, source, desc))
        self.incidents.append({"type": event_type, "severity": severity, "details": desc})

    def generate_report(self):
        # SIEM DB에서 모든 이벤트(DLP 포함) 조회
        cursor = self.conn.cursor()
        cursor.execute("SELECT event_type, severity, source, description, detected_at FROM security_events")
        all_events = [{"type": r[0], "severity": r[1], "source": r[2], "desc": r[3], "time": r[4]} for r in cursor.fetchall()]
        
        report = {
            "generated_at": str(datetime.datetime.now()),
            "total_threats": len(all_events),
            "events": all_events
        }
        with open(INCIDENT_REPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"  ↳ [Report] Full Security Report generated: {INCIDENT_REPORT_PATH}")

# =======================================================
# 🚀 MAIN PIPELINE
# =======================================================
def run_grand_ops_pipeline():
    print("\n" + "█"*60)
    print("🚀 GRAND OPS: DEVSECOPS PIPELINE (v10.0)")
    print("   » Code Scan (DLP) | Threat Intel | SIEM | Forensics")
    print("█"*60 + "\n")
    
    conn = init_db()
    
    # 1. 🛑 PRE-FLIGHT SECURITY SCAN (The New Feature)
    scanner = SecretScanner(conn)
    scanner.seed_leaked_file() # 테스트용 유출 파일 생성
    scanner.scan_workspace()   # 스캔 실행 및 차단 시뮬레이션
    
    # 2. Regular Data Seeding
    print("\n🔄 Initializing System Data...")
    seed_data(conn)
    
    # 3. SOC Runtime Detection
    soc = SecurityOperationsCenter(conn)
    soc.run_detection()
    
    # 4. Final Reporting
    soc.generate_report()
    
    conn.close()
    print("\n✅ Pipeline Finished.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_grand_ops_pipeline()
