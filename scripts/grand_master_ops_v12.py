import sqlite3
import os
import datetime
import hashlib
import shutil
import gzip
import time
import uuid
import json
from cryptography.fernet import Fernet

# =======================================================
# ⚙️ GLOBAL CONFIG & CONSTANTS
# =======================================================
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
BACKUP_DIR = os.path.join(BASE_DIR, "veritas_vault") # Veritas 저장소
LOG_DIR = os.path.join(BASE_DIR, "ctm_logs")         # Control-M 로그

DB_PATH = os.path.join(DATA_DIR, "grand_ops_enterprise.db")
KEY_FILE = os.path.join(CONFIG_DIR, "secret.key")
MIN_WAGE_2025 = 10030

# =======================================================
# 🛡️ VERITAS DATA PROTECTION MODULE
# =======================================================
class VeritasVault:
    """Veritas NetBackup Simulation: 스냅샷, 압축, 무결성 검증"""
    def __init__(self):
        if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)

    def create_snapshot(self, label="DAILY"):
        """DB 파일을 압축하여 백업 저장소에 보관 (Point-in-Time Copy)"""
        if not os.path.exists(DB_PATH): return None
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"snap_{label}_{timestamp}.db.gz"
        target_path = os.path.join(BACKUP_DIR, snapshot_name)
        
        # 압축 백업 실행
        with open(DB_PATH, 'rb') as f_in:
            with gzip.open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 해시 생성 (무결성용)
        file_hash = self._calculate_hash(target_path)
        print(f"  💾 [Veritas] Snapshot Created: {snapshot_name} (Hash: {file_hash[:8]})")
        return target_path

    def _calculate_hash(self, filepath):
        sha = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192): sha.update(chunk)
        return sha.hexdigest()

# =======================================================
# 🎮 CONTROL-M BATCH AUTOMATION MODULE
# =======================================================
class ControlM_Job:
    def __init__(self, job_name, action_func, dependencies=None):
        self.job_name = job_name
        self.action_func = action_func
        self.dependencies = dependencies or []
        self.status = "ORDERED" # ORDERED, EXECUTING, ENDED_OK, ENDED_NOTOK
        self.order_id = str(uuid.uuid4())[:8]
        self.start_time = None
        self.end_time = None

class ControlM_Agent:
    """Control-M Workload Automation Simulation"""
    def __init__(self):
        self.jobs = {}
        if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

    def define_job(self, job_name, func, deps=None):
        self.jobs[job_name] = ControlM_Job(job_name, func, deps)

    def run_flow(self):
        print(f"\n{'='*60}")
        print(f"🕹️ CONTROL-M BATCH SCHEDULE START (New Day Processing)")
        print(f"{'='*60}")
        
        # 의존성 해결을 위한 간단한 순차 실행 로직
        # (실제 Control-M은 DAG 알고리즘을 쓰지만 여기선 정의된 순서대로 체크)
        for name, job in self.jobs.items():
            # 의존성 체크
            can_run = True
            for dep_name in job.dependencies:
                if self.jobs[dep_name].status != "ENDED_OK":
                    print(f"  ⏳ [Hold] Job '{name}' waiting for '{dep_name}'...")
                    can_run = False
                    break
            
            if can_run:
                self._execute_job(job)
            else:
                print(f"  ⛔ [Skip] Job '{name}' skipped due to dependency failure.")

    def _execute_job(self, job):
        job.status = "EXECUTING"
        job.start_time = datetime.datetime.now()
        print(f"\n▶️ [Job Started] {job.job_name} (Order ID: {job.order_id})")
        
        try:
            # 작업 실행
            result = job.action_func()
            
            job.status = "ENDED_OK"
            print(f"  ✅ [Ended OK] {job.job_name} - {result}")
        except Exception as e:
            job.status = "ENDED_NOTOK"
            print(f"  ❌ [Ended NotOK] {job.job_name} - Error: {e}")
        
        job.end_time = datetime.datetime.now()
        self._write_sysout(job)

    def _write_sysout(self, job):
        """작업 로그(Sysout) 파일 기록"""
        log_file = os.path.join(LOG_DIR, f"{job.job_name}_{job.order_id}.log")
        with open(log_file, "w") as f:
            f.write(f"JOB: {job.job_name}\nSTATUS: {job.status}\nSTART: {job.start_time}\nEND: {job.end_time}\n")

# =======================================================
# 🔐 CRYPTO & DB KERNEL (V12)
# =======================================================
class EnterpriseDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._init_crypto()
        self._schema_upgrade()

    def _init_crypto(self):
        if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f: self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f: f.write(self.key)
        self.cipher = Fernet(self.key)

    def encrypt(self, val): return self.cipher.encrypt(str(val).encode()).decode()
    def decrypt(self, val): return self.cipher.decrypt(val.encode()).decode()

    def _schema_upgrade(self):
        # V12 Schema: 인덱싱 및 배치 추적 컬럼 추가
        self.conn.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
        
        # 직원 테이블 (인덱스 추가)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY, comp_id TEXT, enc_name TEXT, enc_account TEXT, 
            base_salary INTEGER, payday_type INTEGER
        )""")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_payday ON employees(payday_type)")

        # 기업 테이블
        self.conn.execute("CREATE TABLE IF NOT EXISTS companies (comp_id TEXT PRIMARY KEY, balance INTEGER)")

        # 거래 원장 (Job ID 추가)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS ledger (
            tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_order_id TEXT,
            prev_hash TEXT,
            curr_hash TEXT,
            sender TEXT, receiver TEXT, enc_amount TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        self.conn.commit()

# =======================================================
# 🏭 BUSINESS LOGIC (PAYROLL & SIMULATION)
# =======================================================
def logic_init_data():
    """JOB 1: 데이터 초기화 및 검증"""
    db = EnterpriseDB()
    if db.conn.execute("SELECT count(*) FROM companies").fetchone()[0] == 0:
        db.conn.execute("INSERT INTO companies VALUES ('SAMSUNG', 9999999999)")
        db.conn.execute("INSERT INTO companies VALUES ('LG', 8888888888)")
        # 11일, 21일 급여 대상자
        db.conn.execute("INSERT INTO employees VALUES ('EMP001', 'SAMSUNG', ?, ?, 4500000, 21)", (db.encrypt("Hong"), db.encrypt("123-456")))
        db.conn.execute("INSERT INTO employees VALUES ('EMP002', 'LG', ?, ?, 2000000, 11)", (db.encrypt("Kim"), db.encrypt("987-654")))
        db.conn.commit()
    return "Data Ready"

def logic_veritas_backup():
    """JOB 2: Veritas 백업 수행"""
    vault = VeritasVault()
    path = vault.create_snapshot(label="PRE_BATCH")
    return f"Backup stored at {os.path.basename(path)}"

def logic_payroll_calc():
    """JOB 3: 급여 계산 및 이체 (핵심 로직)"""
    db = EnterpriseDB()
    today = datetime.datetime.now().day
    # 테스트를 위해 강제 설정 (실제 운영시 주석 처리)
    # today = 21 
    
    targets = db.conn.execute("SELECT * FROM employees WHERE payday_type = ?", (today,)).fetchall()
    
    processed_count = 0
    tx_hash = "GENESIS"
    
    for emp in targets:
        # 최저임금 체크
        if (emp['base_salary'] / 209) < MIN_WAGE_2025:
            print(f"    ⚠️ Min Wage Violation: {emp['emp_id']}")
            continue
            
        # 원장 기록 (Blockchain Chaining)
        last_row = db.conn.execute("SELECT curr_hash FROM ledger ORDER BY tx_id DESC LIMIT 1").fetchone()
        if last_row: tx_hash = last_row[0]
        
        new_data = f"{tx_hash}{emp['emp_id']}{emp['base_salary']}{datetime.datetime.now()}"
        new_hash = hashlib.sha256(new_data.encode()).hexdigest()
        
        db.conn.execute("""
            INSERT INTO ledger (job_order_id, prev_hash, curr_hash, sender, receiver, enc_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("BATCH_JOB_003", tx_hash, new_hash, emp['comp_id'], emp['emp_id'], db.encrypt(emp['base_salary'])))
        
        processed_count += 1
        
    db.conn.commit()
    return f"Processed {processed_count} payrolls for Day {today}"

# =======================================================
# 🚀 MAIN EXECUTOR
# =======================================================
if __name__ == "__main__":
    # 1. Control-M 에이전트 기동
    ctm = ControlM_Agent()

    # 2. 배치 Job Flow 설계 (DAG)
    # JOB_INIT -> JOB_BACKUP -> JOB_PAYROLL
    ctm.define_job("JOB_INIT_DATA", logic_init_data)
    
    ctm.define_job("JOB_VERITAS_BACKUP", logic_veritas_backup, 
                   deps=["JOB_INIT_DATA"]) # Init 성공 시 실행
    
    ctm.define_job("JOB_PAYROLL_ENGINE", logic_payroll_calc, 
                   deps=["JOB_VERITAS_BACKUP"]) # Backup 성공 시 실행

    # 3. 스케줄러 실행
    ctm.run_flow()
    
    # Git 충돌 방지용 클리닝
    if os.path.exists("__pycache__"): shutil.rmtree("__pycache__")
