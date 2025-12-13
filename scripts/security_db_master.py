import sqlite3
import os
import json
import datetime
import re
import base64
import random
import sys
import shutil

# =======================================================
# ⚙️ SYSTEM CONFIGURATION & CONSTANTS
# =======================================================
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")
DB_NAME = "grand_ops_secure.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "db_engine_conf.json")
SCHEMA_DUMP_FILE = os.path.join(DATA_DIR, "schema_snapshot.sql")

# [보안] 난독화된 패턴 (소스코드 스캔 오탐지 방지)
PATTERNS_B64 = {
    "AWS_ACCESS_KEY": "QUtJQVswLTlBLVpdezE2fQ==", 
    "SSH_PRIVATE_KEY": "LS0tLS1CRUdJTiAoUlNBfDVEU0F8RUN8T1BFTlNTSCkgUFJJVkFURSBLRVktLS0tLQ=="
}

# =======================================================
# 📜 MIGRATION PLANS (Schema Version Control)
# =======================================================
# 마이그레이션 스크립트 정의 (버전별 변경 사항)
MIGRATIONS = {
    1: [
        """CREATE TABLE IF NOT EXISTS schema_versions (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE IF NOT EXISTS security_logic (id INTEGER PRIMARY KEY AUTOINCREMENT, rule_name TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    ],
    2: [
        """ALTER TABLE security_logic ADD COLUMN severity_level TEXT DEFAULT 'LOW'""",
        """ALTER TABLE security_logic ADD COLUMN detected_area TEXT DEFAULT 'UNKNOWN'"""
    ],
    3: [
        """ALTER TABLE security_logic ADD COLUMN action_taken TEXT DEFAULT 'LOG_ONLY'""",
        """CREATE TABLE IF NOT EXISTS audit_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, status TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    ],
    4: [
        """CREATE INDEX IF NOT EXISTS idx_severity ON security_logic(severity_level)""",
        """CREATE INDEX IF NOT EXISTS idx_created_at ON security_logic(created_at)"""
    ]
}

# =======================================================
# 🛠️ INFRASTRUCTURE & PROVISIONING MANAGER
# =======================================================
class InfraManager:
    @staticmethod
    def provision_environment():
        """서버 환경 구성 및 디렉터리 권한 설정 (Installation)"""
        print("🏗️ [Infra] Provisioning DB Environment...")
        
        # 1. 필수 디렉터리 생성
        for d in [DATA_DIR, CONFIG_DIR, BACKUP_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
                print(f"  ↳ Created directory: {d}")
            
            # [Security] 권한 강화 (Linux/Unix 환경)
            if os.name == 'posix':
                os.chmod(d, 0o700) # rwx------ (소유자만 접근 가능)

        # 2. 설정 파일 생성 (Configuration Management)
        config_data = {
            "engine_version": "3.0.0",
            "db_path": DB_PATH,
            "max_connections": 10,
            "maintenance_window": "02:00-04:00",
            "last_provisioned": str(datetime.datetime.now())
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        print("  ↳ Configuration file generated.")

    @staticmethod
    def snapshot_schema(conn):
        """현재 DB 스키마를 SQL 파일로 덤프 (형상 관리용)"""
        print("📸 [CM] Taking Schema Snapshot...")
        try:
            with open(SCHEMA_DUMP_FILE, 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
            print(f"  ↳ Schema dumped to {SCHEMA_DUMP_FILE}")
        except Exception as e:
            print(f"  ⚠️ Schema dump failed: {e}")

# =======================================================
# 🚀 DATABASE ENGINE & MIGRATOR
# =======================================================
class DBEngine:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def get_current_version(self):
        """현재 적용된 스키마 버전 확인"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MAX(version) FROM schema_versions")
            ver = cur.fetchone()[0]
            return ver if ver is not None else 0
        except sqlite3.OperationalError:
            return 0

    def run_migrations(self):
        """버전 기반 자동 마이그레이션 실행"""
        print("🔄 [DB] Checking for Schema Migrations...")
        current_ver = self.get_current_version()
        latest_ver = max(MIGRATIONS.keys())

        if current_ver >= latest_ver:
            print(f"  ✅ Database is up-to-date (Version {current_ver}).")
            return

        print(f"  ⚠️ Current Version: {current_ver} -> Target: {latest_ver}")
        
        for ver in range(current_ver + 1, latest_ver + 1):
            print(f"  🚀 Applying Migration v{ver}...")
            try:
                for sql in MIGRATIONS[ver]:
                    self.conn.execute(sql)
                
                # 버전 기록
                self.conn.execute("INSERT INTO schema_versions (version) VALUES (?)", (ver,))
                self.conn.commit()
                print(f"    - v{ver} Applied Successfully.")
            except Exception as e:
                print(f"    ❌ Migration v{ver} FAILED: {e}")
                sys.exit(1) # 마이그레이션 실패 시 즉시 중단 (데이터 보호)

    def simulate_operations(self):
        """데이터 처리 시뮬레이션 (Traffic Generation)"""
        print("📊 [Ops] Processing Security Telemetry...")
        cursor = self.conn.cursor()
        
        actions = ["BLOCKED", "QUARANTINED", "ALERTED", "DROPPED"]
        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        
        # Data Ingestion
        for _ in range(random.randint(5, 10)):
            cursor.execute('''
                INSERT INTO security_logic (rule_name, severity_level, detected_area, action_taken)
                VALUES (?, ?, ?, ?)
            ''', (
                f"SIG-{random.randint(1000,9999)}",
                random.choice(severities),
                "Firewall_Zone_A",
                random.choice(actions)
            ))
        
        # Data Pruning (Optimization Prep)
        cursor.execute("DELETE FROM security_logic WHERE id % 20 == 0")
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

# =======================================================
# 🕵️‍♂️ SECURITY & COMPLIANCE SCANNER
# =======================================================
def get_pattern(name):
    return base64.b64decode(PATTERNS_B64[name]).decode('utf-8')

def run_security_scan():
    print("\n🔍 [Sec] Running Internal Security Scan...")
    
    SKIP_DIRS = {'.git', '.github', 'backup', 'scripts', '__pycache__', 'config', 'data'}
    SKIP_EXTS = {'.db', '.bak', '.sql', '.json', '.pyc'}
    
    patterns = {
        "AWS": get_pattern("AWS_ACCESS_KEY"),
        "SSH": get_pattern("SSH_PRIVATE_KEY")
    }
    
    issues = 0
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            if os.path.splitext(file)[1] in SKIP_EXTS: continue
            if file == os.path.basename(__file__): continue
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', errors='ignore') as f:
                    content = f.read()
                    for name, pat in patterns.items():
                        if re.search(pat, content):
                            print(f"  ⚠️  [ALERT] Potential {name} Key in: {filepath}")
                            issues += 1
            except: pass
            
    if issues == 0:
        print("  ✅ Security Scan Passed.")
    else:
        print(f"  ⚠️  Found {issues} potential issues.")

# =======================================================
# 🎬 ENTRY POINT
# =======================================================
if __name__ == "__main__":
    print(f"🚀 Security DB Master Started: {datetime.datetime.now()}")
    
    # 1. 인프라 프로비저닝 (설치 및 환경구성)
    InfraManager.provision_environment()
    
    # 2. DB 엔진 구동 및 마이그레이션
    engine = DBEngine()
    engine.connect()
    engine.run_migrations()
    
    # 3. 데이터 오퍼레이션 수행
    engine.simulate_operations()
    
    # 4. 형상 관리 (스키마 스냅샷 저장)
    InfraManager.snapshot_schema(engine.conn)
    
    engine.close()
    
    # 5. 보안 스캔
    run_security_scan()
    
    print("✅ System Shutdown Gracefully.")
