import sqlite3
import os
import json
import datetime
import re
import base64
import random
import sys
import shutil
import stat  # [Security] 권한 제어를 위한 모듈 추가

# =======================================================
# ⚙️ SYSTEM CONFIGURATION
# =======================================================
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")
DB_NAME = "grand_ops_secure.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "db_engine_conf.json")
SCHEMA_DUMP_FILE = os.path.join(DATA_DIR, "schema_snapshot.sql")

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
# 🔐 SECURITY DEFENSE LAYER (Grand Ops Logic)
# =======================================================
class SecurityGuardian:
    @staticmethod
    def enforce_permissions(path, is_dir=False):
        """
        [Critical] 파일/디렉토리 권한 강제 설정
        - Directory: 700 (drwx------) : 소유자만 진입 가능
        - File: 600 (-rw-------) : 소유자만 읽기/쓰기 가능
        """
        if not os.path.exists(path):
            return

        try:
            if is_dir:
                # 디렉터리: 소유자만 실행/읽기/쓰기 (rwx------)
                os.chmod(path, stat.S_IRWXU)
            else:
                # 파일: 소유자만 읽기/쓰기 (rw-------)
                os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
            
            # (옵션) 디버깅용 로그 (보안상 실제로는 조용히 처리하는 것이 좋음)
            # print(f"  🔒 Locked down: {os.path.basename(path)}")
        except Exception as e:
            print(f"  ⚠️ Security Warning: Failed to chmod {path}: {e}")

class InfraManager:
    @staticmethod
    def provision_environment():
        """환경 구성 (Idempotent + Security Hardening)"""
        print("🏗️ [Infra] Provisioning Secure Environment...")
        
        # 1. 디렉토리 보안 생성
        for d in [DATA_DIR, CONFIG_DIR, BACKUP_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
            # 생성 후 즉시 권한 700 적용
            SecurityGuardian.enforce_permissions(d, is_dir=True)

        # 2. 설정 파일 관리
        new_config = {
            "engine_version": "3.1.0",
            "db_path": DB_PATH,
            "max_connections": 20,
            "policy": "strict_isolation",
            "access_control": "owner_only"
        }
        
        should_write = True
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    current_config = json.load(f)
                if current_config == new_config:
                    should_write = False
            except: pass
            
        if should_write:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(new_config, f, indent=4)
            print("  ↳ Configuration updated.")
        
        # [Security] 설정 파일 권한 600 강제 (생성 혹은 수정 후)
        SecurityGuardian.enforce_permissions(CONFIG_FILE, is_dir=False)

    @staticmethod
    def snapshot_schema(conn):
        """스키마 스냅샷 및 보안 저장"""
        try:
            with open(SCHEMA_DUMP_FILE, 'w') as f:
                temp_dump = ""
                for line in conn.iterdump():
                    temp_dump += f"{line}\n"
                f.write(temp_dump)
            
            # [Security] 덤프 파일 권한 600 강제
            SecurityGuardian.enforce_permissions(SCHEMA_DUMP_FILE, is_dir=False)
            
        except Exception as e:
            print(f"  ⚠️ Schema dump warning: {e}")

class DBEngine:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        # 연결 시점에 파일이 생성되므로 연결 직후 권한 검사 수행
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        
        # [Security] DB 파일이 존재하면 즉시 권한 600 강제
        if os.path.exists(DB_PATH):
            SecurityGuardian.enforce_permissions(DB_PATH, is_dir=False)

    def get_current_version(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MAX(version) FROM schema_versions")
            ver = cur.fetchone()[0]
            return ver if ver is not None else 0
        except: return 0

    def run_migrations(self):
        current_ver = self.get_current_version()
        latest_ver = max(MIGRATIONS.keys())
        if current_ver < latest_ver:
            print(f"🔄 Applying Migrations v{current_ver+1} to v{latest_ver}...")
            for ver in range(current_ver + 1, latest_ver + 1):
                try:
                    for sql in MIGRATIONS[ver]: self.conn.execute(sql)
                    self.conn.execute("INSERT INTO schema_versions (version) VALUES (?)", (ver,))
                    self.conn.commit()
                except Exception as e:
                    print(f"❌ Migration v{ver} Failed: {e}")
                    sys.exit(1)

    def simulate_operations(self):
        cursor = self.conn.cursor()
        print("📊 Processing Secured Data Transaction...")
        # 데이터 적재
        for _ in range(random.randint(1, 5)):
            cursor.execute('''
                INSERT INTO security_logic (rule_name, severity_level, detected_area, action_taken)
                VALUES (?, ?, ?, ?)
            ''', (f"R-{random.randint(100,999)}", "MEDIUM", "INTERNAL_NET", "ISOLATE"))
        
        # 데이터 정리
        cursor.execute("DELETE FROM security_logic WHERE id IN (SELECT id FROM security_logic ORDER BY random() LIMIT 2)")
        self.conn.commit()

    def close(self):
        if self.conn: self.conn.close()

if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"🚀 GRAND OPS MASTER ENGINE START: {datetime.datetime.now()}")
    print(f"🛡️  SECURITY PROTOCOL: STRICT (CHMOD 600/700)")
    print(f"{'='*50}\n")
    
    InfraManager.provision_environment()
    
    engine = DBEngine()
    engine.connect()
    engine.run_migrations()
    engine.simulate_operations()
    InfraManager.snapshot_schema(engine.conn)
    engine.close()
    
    print("\n✅ Engine Task Completed Successfully.")
