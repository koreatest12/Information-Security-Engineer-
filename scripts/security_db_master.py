import sqlite3
import os
import json
import datetime
import random
import sys
import stat
import multiprocessing
import subprocess
import hashlib
import uuid

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
DEP_LOCK_FILE = os.path.join(CONFIG_DIR, "requirements.lock")
DEP_GRAPH_FILE = os.path.join(CONFIG_DIR, "dependency_graph.json")
GITIGNORE_FILE = os.path.join(BASE_DIR, ".gitignore")

# 마이그레이션 SQL 목록
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
    ],
    5: [
        """CREATE TABLE IF NOT EXISTS server_health (check_id INTEGER PRIMARY KEY AUTOINCREMENT, cpu_load REAL, memory_usage REAL, checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
        """INSERT INTO security_logic (rule_name, severity_level, action_taken) VALUES ('SYS_INIT', 'INFO', 'SYSTEM_UPGRADE_COMPLETE')"""
    ],
    6: [
        """CREATE TABLE IF NOT EXISTS dependency_tracker (track_id INTEGER PRIMARY KEY AUTOINCREMENT, package_name TEXT, version TEXT, hash_sign TEXT, tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    ]
}

# =======================================================
# 🛡️ DEFENSE & OPS MODULES
# =======================================================
class SecurityGuardian:
    @staticmethod
    def enforce_permissions(path, is_dir=False):
        if not os.path.exists(path): return
        try:
            if is_dir: os.chmod(path, stat.S_IRWXU)
            else: os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception: pass

class GitOpsManager:
    """[NEW] Git 설정 자동 보정 및 무시 규칙 관리자"""
    @staticmethod
    def enforce_gitignore_policy():
        print("🔧 [GitOps] Checking .gitignore Policy...")
        # .gitignore가 없으면 생성
        if not os.path.exists(GITIGNORE_FILE):
            with open(GITIGNORE_FILE, "w") as f:
                f.write("*.pyc\n__pycache__/\n")
        
        # 핵심 파일이 무시되지 않도록 화이트리스트 규칙 확인
        needed_rules = [
            f"!data/{DB_NAME}",   # DB 파일 추적 허용
            f"!data/*.sql",       # SQL 스냅샷 허용
            f"!config/*.lock",    # Lock 파일 허용
            f"!config/*.json"     # 설정 파일 허용
        ]
        
        try:
            with open(GITIGNORE_FILE, "r") as f:
                content = f.read()
            
            updated = False
            with open(GITIGNORE_FILE, "a") as f:
                for rule in needed_rules:
                    if rule not in content:
                        f.write(f"\n{rule} # Auto-added by DB Master Bot")
                        updated = True
                        print(f"  ↳ Added Whitelist Rule: {rule}")
            
            if not updated:
                print("  ✅ .gitignore Policy is Up-to-Date.")
                
        except Exception as e:
            print(f"  ⚠️ GitOps Warning: Could not update .gitignore - {e}")

class DependencyTracker:
    def __init__(self, conn):
        self.conn = conn

    def snapshot_environment(self):
        print("📦 [Dependency] Generating Environment Snapshot...")
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
            dependencies = result.stdout.strip().split('\n')
            
            with open(DEP_LOCK_FILE, 'w', encoding='utf-8') as f:
                f.write("# GRAND OPS AUTO-GENERATED LOCK FILE\n")
                f.write(f"# Generated at: {datetime.datetime.now()}\n")
                f.write(result.stdout)
            SecurityGuardian.enforce_permissions(DEP_LOCK_FILE)

            dep_list = []
            for dep in dependencies:
                if '==' in dep:
                    pkg, ver = dep.split('==', 1)
                    pkg_hash = hashlib.sha256(f"{pkg}:{ver}".encode()).hexdigest()
                    dep_list.append({"package": pkg, "version": ver, "signature": pkg_hash})
                    self.conn.execute("INSERT INTO dependency_tracker (package_name, version, hash_sign) VALUES (?, ?, ?)",
                                      (pkg, ver, pkg_hash))
            
            with open(DEP_GRAPH_FILE, 'w', encoding='utf-8') as f:
                json.dump({"snapshot_id": str(uuid.uuid4()), "packages": dep_list}, f, indent=4)
            
            self.conn.commit()
            print(f"  ✅ Snapshot Saved: {len(dep_list)} packages tracked.")

        except Exception as e:
            print(f"  ⚠️ Dependency Snapshot Failed: {e}")

class ServerOps:
    @staticmethod
    def optimize_db_config(conn):
        try:
            cpu_count = multiprocessing.cpu_count()
            if cpu_count >= 2:
                conn.execute("PRAGMA cache_size = -4000;")
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
                conn.execute("PRAGMA temp_store = MEMORY;")
                print(f"  ⚡ [Tuning] High-Performance Mode (CPUs: {cpu_count})")
            else:
                print("  ℹ️ [Tuning] Standard Mode Active.")
        except Exception: pass

class MigrationManager:
    def __init__(self, conn):
        self.conn = conn

    def get_current_version(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MAX(version) FROM schema_versions")
            ver = cur.fetchone()[0]
            return ver if ver is not None else 0
        except: return 0

    def run(self):
        current_ver = self.get_current_version()
        latest_ver = max(MIGRATIONS.keys())
        if current_ver < latest_ver:
            print(f"🔄 [Migration] Starting Upgrade v{current_ver} -> v{latest_ver}...")
            for ver in range(current_ver + 1, latest_ver + 1):
                try:
                    self.conn.execute("BEGIN TRANSACTION;")
                    for sql in MIGRATIONS[ver]:
                        self.conn.execute(sql)
                    self.conn.execute("INSERT INTO schema_versions (version) VALUES (?)", (ver,))
                    self.conn.commit()
                    print(f"    ✅ v{ver} Applied.")
                except Exception as e:
                    self.conn.rollback()
                    print(f"    ❌ v{ver} Failed! Rolled back.")
                    sys.exit(1)

class DBEngine:
    def __init__(self):
        self.conn = None
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        SecurityGuardian.enforce_permissions(DB_PATH)
    def close(self):
        if self.conn: self.conn.close()

# =======================================================
# 🚀 MAIN EXECUTION
# =======================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"🚀 GRAND OPS MASTER ENGINE V9 (GITOPS & FORCE SYNC)")
    print(f"{'='*60}\n")
    
    # 1. 인프라 체크 및 GitOps 정책 적용
    print("🏗️ [Infra] Checking Environment & Git Policy...")
    for d in [DATA_DIR, CONFIG_DIR, BACKUP_DIR]:
        if not os.path.exists(d): os.makedirs(d)
        SecurityGuardian.enforce_permissions(d, is_dir=True)
    
    # [FIX] .gitignore 자동 보정 실행
    GitOpsManager.enforce_gitignore_policy()
    
    # 2. DB 연결 및 작업
    engine = DBEngine()
    engine.connect()
    ServerOps.optimize_db_config(engine.conn)
    
    migrator = MigrationManager(engine.conn)
    migrator.run()

    dep_tracker = DependencyTracker(engine.conn)
    dep_tracker.snapshot_environment()
    
    # 데이터 시뮬레이션
    engine.conn.execute("INSERT INTO security_logic (rule_name, severity_level, action_taken) VALUES (?, ?, ?)", 
                        (f"AUTO-DEFENSE-{random.randint(10000,99999)}", "CRITICAL", "ISOLATE_HOST"))
    engine.conn.commit()
    
    with open(SCHEMA_DUMP_FILE, 'w') as f:
        for line in engine.conn.iterdump(): f.write(f"{line}\n")
    SecurityGuardian.enforce_permissions(SCHEMA_DUMP_FILE)
    
    engine.close()
    print("\n✅ System Ready for Force-Push.")
