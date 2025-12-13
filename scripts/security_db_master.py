import sqlite3
import os
import json
import datetime
import random
import sys
import stat
import multiprocessing

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
    5: [ # [NEW] 새로운 마이그레이션 추가
        """CREATE TABLE IF NOT EXISTS server_health (check_id INTEGER PRIMARY KEY AUTOINCREMENT, cpu_load REAL, memory_usage REAL, checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
        """INSERT INTO security_logic (rule_name, severity_level, action_taken) VALUES ('SYS_INIT', 'INFO', 'SYSTEM_UPGRADE_COMPLETE')"""
    ]
}

# =======================================================
# 🛡️ DEFENSE & OPS MODULES
# =======================================================
class SecurityGuardian:
    @staticmethod
    def enforce_permissions(path, is_dir=False):
        """권한 강제 (chmod 600 / 700)"""
        if not os.path.exists(path): return
        try:
            if is_dir: os.chmod(path, stat.S_IRWXU) # 700
            else: os.chmod(path, stat.S_IRUSR | stat.S_IWUSR) # 600
        except Exception: pass

class ServerOps:
    """[NEW] 서버 상태 진단 및 DB 튜닝 매니저"""
    @staticmethod
    def optimize_db_config(conn):
        """하드웨어 사양에 따른 DB 파라미터 튜닝"""
        try:
            cpu_count = multiprocessing.cpu_count()
            # CPU가 많으면 병렬 처리 및 캐시 증설
            if cpu_count >= 2:
                # Cache Size: 2000 pages -> ~8MB (기본값보다 상향)
                conn.execute("PRAGMA cache_size = -2000;") 
                # 저널 모드: WAL (Write-Ahead Logging) -> 동시성 향상
                conn.execute("PRAGMA journal_mode = WAL;")
                # 동기화 모드: NORMAL (안전성과 성능 균형)
                conn.execute("PRAGMA synchronous = NORMAL;")
                print(f"  ⚡ [Tuning] Server Upgrade Applied: WAL Mode, Cache Optimized (CPUs: {cpu_count})")
            else:
                print("  ℹ️ [Tuning] Standard Mode Active.")
        except Exception as e:
            print(f"  ⚠️ Tuning Warning: {e}")

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
                print(f"  ↳ Applying v{ver}...")
                try:
                    # 트랜잭션 시작
                    self.conn.execute("BEGIN TRANSACTION;")
                    for sql in MIGRATIONS[ver]:
                        self.conn.execute(sql)
                    
                    self.conn.execute("INSERT INTO schema_versions (version) VALUES (?)", (ver,))
                    self.conn.commit() # 성공 시 커밋
                    print(f"    ✅ v{ver} Success.")
                except Exception as e:
                    self.conn.rollback() # 실패 시 롤백
                    print(f"    ❌ v{ver} Failed! Rolled back. Error: {e}")
                    sys.exit(1)
        else:
            print("✅ [Migration] Schema is up-to-date.")

class DBEngine:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        # 연결 즉시 권한 보호
        SecurityGuardian.enforce_permissions(DB_PATH)

    def close(self):
        if self.conn: self.conn.close()

# =======================================================
# 🚀 MAIN EXECUTION
# =======================================================
if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"🚀 GRAND OPS MASTER ENGINE V7 (UPGRADE & MIGRATE)")
    print(f"{'='*50}\n")
    
    # 1. 환경 구성 및 보안 권한 설정
    print("🏗️ [Infra] Checking Environment...")
    for d in [DATA_DIR, CONFIG_DIR, BACKUP_DIR]:
        if not os.path.exists(d): os.makedirs(d)
        SecurityGuardian.enforce_permissions(d, is_dir=True)
    
    # 2. DB 연결
    engine = DBEngine()
    engine.connect()
    
    # 3. [NEW] 서버 사양에 따른 DB 엔진 튜닝 (업그레이드)
    ServerOps.optimize_db_config(engine.conn)
    
    # 4. [NEW] 고도화된 마이그레이션 실행
    migrator = MigrationManager(engine.conn)
    migrator.run()
    
    # 5. 데이터 시뮬레이션
    print("📊 [Ops] Processing Data Transactions...")
    engine.conn.execute("INSERT INTO security_logic (rule_name, severity_level, action_taken) VALUES (?, ?, ?)", 
                        (f"AUTO-BLOCK-{random.randint(1000,9999)}", "HIGH", "FIREWALL_DROP"))
    engine.conn.commit()
    
    # 6. 스키마 스냅샷 저장
    with open(SCHEMA_DUMP_FILE, 'w') as f:
        for line in engine.conn.iterdump(): f.write(f"{line}\n")
    SecurityGuardian.enforce_permissions(SCHEMA_DUMP_FILE)
    
    engine.close()
    print("\n✅ System Upgrade & Operations Completed Successfully.")
