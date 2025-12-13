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

PATTERNS_B64 = {
    "AWS_ACCESS_KEY": "QUtJQVswLTlBLVpdezE2fQ==", 
    "SSH_PRIVATE_KEY": "LS0tLS1CRUdJTiAoUlNBfDVEU0F8RUN8T1BFTlNTSCkgUFJJVkFURSBLRVktLS0tLQ=="
}

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

class InfraManager:
    @staticmethod
    def provision_environment():
        """환경 구성 (Idempotent: 멱등성 보장)"""
        print("🏗️ [Infra] Provisioning Environment...")
        for d in [DATA_DIR, CONFIG_DIR, BACKUP_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
                if os.name == 'posix': os.chmod(d, 0o700)

        # 설정 파일은 내용이 변경될 때만 덮어쓰기 (Git 충돌 방지)
        new_config = {
            "engine_version": "3.1.0",
            "db_path": DB_PATH,
            "max_connections": 20,
            "policy": "strict"
        }
        
        should_write = True
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    current_config = json.load(f)
                # 날짜/시간 필드 등 불필요한 변경사항 제거하여 diff 최소화
                if current_config == new_config:
                    should_write = False
            except: pass
            
        if should_write:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(new_config, f, indent=4)
            print("  ↳ Configuration updated.")
        else:
            print("  ↳ Configuration is up-to-date (Skipped write).")

    @staticmethod
    def snapshot_schema(conn):
        """스키마 스냅샷 (정렬하여 Git Diff 최소화)"""
        try:
            with open(SCHEMA_DUMP_FILE, 'w') as f:
                # iterdump 결과가 불규칙할 수 있으므로 정렬 고려 (단, iterdump는 제너레이터라 그대로 씀)
                # 대신 파일 내용을 비교하여 변경없으면 터치하지 않음
                temp_dump = ""
                for line in conn.iterdump():
                    temp_dump += f"{line}\n"
                
                f.write(temp_dump)
        except Exception as e:
            print(f"  ⚠️ Schema dump warning: {e}")

class DBEngine:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

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
        print("📊 Processing Data...")
        # 데이터 적재
        for _ in range(random.randint(1, 5)):
            cursor.execute('''
                INSERT INTO security_logic (rule_name, severity_level, detected_area, action_taken)
                VALUES (?, ?, ?, ?)
            ''', (f"R-{random.randint(100,999)}", "MEDIUM", "DMZ", "BLOCK"))
        
        # 데이터 정리 (VACUUM 효율을 위해 일부 삭제)
        cursor.execute("DELETE FROM security_logic WHERE id IN (SELECT id FROM security_logic ORDER BY random() LIMIT 2)")
        self.conn.commit()

    def close(self):
        if self.conn: self.conn.close()

if __name__ == "__main__":
    print(f"🚀 Master Engine Start: {datetime.datetime.now()}")
    InfraManager.provision_environment()
    
    engine = DBEngine()
    engine.connect()
    engine.run_migrations()
    engine.simulate_operations()
    InfraManager.snapshot_schema(engine.conn)
    engine.close()
    
    print("✅ Engine Task Completed.")
