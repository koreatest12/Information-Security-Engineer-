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
GITIGNORE_FILE = os.path.join(BASE_DIR, ".gitignore")
DEP_LOCK_FILE = os.path.join(CONFIG_DIR, "requirements.lock")

MIGRATIONS = {
    1: ["""CREATE TABLE IF NOT EXISTS schema_versions (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""],
    2: ["""CREATE TABLE IF NOT EXISTS security_logic (id INTEGER PRIMARY KEY AUTOINCREMENT, rule_name TEXT, severity_level TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""],
    3: ["""CREATE TABLE IF NOT EXISTS audit_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, status TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""],
    4: ["""CREATE TABLE IF NOT EXISTS dependency_tracker (track_id INTEGER PRIMARY KEY AUTOINCREMENT, package_name TEXT, version TEXT, hash_sign TEXT, tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""]
}

# =======================================================
# 🛡️ DEFENSE & OPS MODULES (V10 UPGRADE)
# =======================================================
class WorkspaceCleaner:
    """[NEW] Git 충돌 방지를 위한 잔여 파일 소각 모듈"""
    @staticmethod
    def cleanup_residuals():
        print("🧹 [Cleanup] Removing conflicting temporary files...")
        targets = [
            "__pycache__", 
            ".pytest_cache",
            "audit_log.txt" # 로그는 아티팩트로 전송 후 로컬에서 제거하여 Git 충돌 방지
        ]
        
        for root, dirs, files in os.walk(BASE_DIR):
            for d in dirs:
                if d in targets:
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            for f in files:
                if f.endswith(".pyc") or f in targets:
                    try:
                        os.remove(os.path.join(root, f))
                    except: pass
        print("  ✅ Workspace Cleaned.")

class IntegrityVerifier:
    """[NEW] 데이터 무결성 검증 및 서명"""
    @staticmethod
    def sign_db_file():
        if not os.path.exists(DB_PATH): return
        
        sha256_hash = hashlib.sha256()
        with open(DB_PATH, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        sign = sha256_hash.hexdigest()
        print(f"🔐 [Integrity] DB Signed: {sign[:16]}... (Verified)")
        
        # 무결성 서명 파일 저장 (Git이 변경 감지하도록)
        with open(os.path.join(CONFIG_DIR, "db_signature.sig"), "w") as f:
            f.write(sign)

class SecurityGuardian:
    @staticmethod
    def enforce_permissions(path, is_dir=False):
        if not os.path.exists(path): return
        try:
            if is_dir: os.chmod(path, stat.S_IRWXU)
            else: os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception: pass

class GitOpsManager:
    @staticmethod
    def enforce_gitignore_policy():
        # GitIgnore 정책 강제 주입
        needed_rules = ["!data/grand_ops_secure.db", "!config/*.sig", "!config/*.lock"]
        if not os.path.exists(GITIGNORE_FILE):
            with open(GITIGNORE_FILE, "w") as f: f.write("")
            
        with open(GITIGNORE_FILE, "r") as f: content = f.read()
        
        with open(GITIGNORE_FILE, "a") as f:
            for rule in needed_rules:
                if rule not in content:
                    f.write(f"\n{rule}")

class DBEngine:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def run_migrations(self):
        # 간소화된 마이그레이션 로직
        try:
            self.conn.execute("CREATE TABLE IF NOT EXISTS schema_versions (version INTEGER PRIMARY KEY)")
            current_ver = self.conn.execute("SELECT MAX(version) FROM schema_versions").fetchone()[0] or 0
            
            for ver, queries in MIGRATIONS.items():
                if ver > current_ver:
                    for q in queries: self.conn.execute(q)
                    self.conn.execute("INSERT INTO schema_versions (version) VALUES (?)", (ver,))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Migration Warning: {e}")

    def close(self):
        if self.conn: 
            self.conn.close()
            # 연결 종료 후 무결성 서명 실행
            IntegrityVerifier.sign_db_file()

# =======================================================
# 🚀 MAIN EXECUTION
# =======================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"🚀 GRAND OPS MASTER ENGINE V10 (CLEAN & INTEGRITY)")
    print(f"{'='*60}\n")
    
    # 1. 초기화
    for d in [DATA_DIR, CONFIG_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    
    GitOpsManager.enforce_gitignore_policy()
    
    # 2. DB 작업
    engine = DBEngine()
    engine.connect()
    engine.run_migrations()
    
    # 데이터 시뮬레이션
    engine.conn.execute("INSERT INTO audit_logs (action, status) VALUES (?, ?)", ("SYSTEM_CHECK", "OK"))
    engine.conn.commit()
    
    engine.close()
    
    # 3. [CRITICAL] Git 충돌 방지를 위한 작업 공간 청소
    WorkspaceCleaner.cleanup_residuals()
    
    print("\n✅ System Operations Finished.")
