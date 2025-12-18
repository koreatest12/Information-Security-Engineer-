import sqlite3
import pandas as pd
import os
import urllib.request
import numpy as np  # 랜덤 데이터 생성용
from datetime import datetime

# [시각화 라이브러리]
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# [PDF 생성 및 암호화 라이브러리]
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pdfencrypt import StandardEncryption

# ==========================================
# 1. DB 매니저: 데이터베이스 초기화 및 관리
# ==========================================
class PayrollDBManager:
    def __init__(self, db_name="payroll.db"):
        self.db_name = db_name

    def initialize_db(self):
        """DB 테이블 생성 및 기초 데이터 입력"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 사원 마스터 테이블 (변하지 않는 정보)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dept TEXT,
                email TEXT,
                birth_date TEXT,
                base_pay INTEGER, 
                bank_name TEXT,
                account_number TEXT
            )
        ''')
        
        # 샘플 데이터 (중복 시 무시: OR IGNORE)
        sample_data = [
            ('2025001', '김철수', '개발팀', 'kim@test.com', '900101', 5000000, '국민은행', '111-111'),
            ('2025002', '이영희', '인사팀', 'lee@test.com', '920505', 4500000, '신한은행', '222-222'),
            ('2025003', '박민수', '영업팀', 'park@test.com', '881212', 5500000, '우리은행', '333-333'),
            ('2025004', '최지수', '디자인', 'choi@test.com', '950303', 4200000, '카카오뱅크', '444-444'),
            ('2025005', '정우성', '개발팀', 'jung@test.com', '850707', 6000000, '하나은행', '555-555')
        ]
        
        cursor.executemany('INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?,?,?,?)', sample_data)
        conn.commit()
        conn.close()
        print(f">> [DB] '{self.db_name}' 연결 및 초기화 완료.")

# ==========================================
# 2. 메인 워크플로우: 데이터 병합, 계산, 출력
# ==========================================
class MasterPayrollWorkflow:
    def __init__(self, db_name="payroll.db"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 급여 시스템 가동...")
        self.db_name = db_name
        self.current_month = datetime.now().strftime('%Y-%m')
        self.output_dir = f"Payroll_Result_{self.current_month}"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 한글 폰트 설정 (자동 다운로드 포함)
        self._setup_korean_font()

    def _setup_korean_font(self):
        """OS 무관 한글 폰트(나눔고딕) 자동 다운로드 및 설정"""
        self.font_name = 'NanumGothic'
        font_file = 'NanumGothic.ttf'
        
        # 1. 폰트 파일 없으면 다운로드
        if not os.path.exists(font_file):
            print(">> 한글 폰트 다운로드 중... (NanumGothic)")
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_file)
        
        # 2. PDF용 폰트 등록
        try:
            pdfmetrics.registerFont(TTFont(self.font_name, font_file))
        except:
            self.font_name = 'Helvetica' # 실패 시 영문 기본값
            
        # 3. 그래프용 폰트 등록
        try:
            fe = fm.FontEntry(fname=font_file, name=self.font_name)
            fm.fontManager.ttflist.insert(0, fe)
            plt.rc('font', family=self.font_name)
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass

    def load_and_merge_data(self):
        """[Step 1] DB(마스터) + 엑셀/변동데이터(야근) 병합"""
        print(">> 1. 데이터 로드 및 병합 (DB + Variable Data)")
        
        # 1. DB에서 사원 정보 가져오기
        conn = sqlite3.connect(self.db_name)
        df_master = pd.read_sql("SELECT * FROM employees", conn)
        conn.close()
        
        # 2. 이번 달 변동 데이터 생성 (실무에선 엑셀 로드)
        # 시뮬레이션: 각 사원별로 0 ~ 500,000원 사이의 야근 수당 랜덤 배정
        print("   - (Note) 이번 달 야근 수당 데이터를 생성합니다.")
        np.random.seed(42) # 결과 재현을 위해 시드 고정
        variable_data = {
            'emp_id': df_master['emp_id'],
            'overtime_pay': np.random.randint(0, 6, size=len(df_master)) * 100000
        }
        df_variable = pd.DataFrame(variable_data)
        
        # 3. 데이터 병합 (Left Join)
        self.df = pd.merge(df_master, df_variable, on='emp_id', how='left')
        self.df['overtime_pay'] = self.df['overtime_pay'].fillna(0) # 결측치 0원 처리

    def calculate_payroll(self):
        """[Step 2] 급여 및 세금 정밀 계산"""
        print(">> 2. 급여 계산 엔진 실행")
        
        # 비과세(식대 20만원) 적용
        tax_free = 200000
        self.df['taxable'] = self.df['base_pay'] + self.df['overtime_pay'] - tax_free
        
        # 4대 보험 (요율 적용)
        self.df['pension'] = (self.df['taxable'] * 0.045).astype(int)
        self.df['health'] = (self.df['taxable'] * 0.03545).astype(int)
        self.df['care'] = (self.df['health'] * 0.1295).astype(int)
        self.df['employ'] = (self.df['taxable'] * 0.009).astype(int)
        
        # 소득세 (간이 3% 가정)
        self.df['income_tax'] = (self.df['taxable'] * 0.03).astype(int)
        self.df['local_tax'] = (self.df['income_tax'] * 0.1).astype(int)
        
        # 합계 도출
        self.df['total_deduct'] = (self.df['pension'] + self.df['health'] + self.df['care'] + 
                                   self.df['employ'] + self.df['income_tax'] + self.df['local_tax'])
        self.df['total_pay'] = self.df['base_pay'] + self.df['overtime_pay']
        self.df['net_pay'] = self.df['total_pay'] - self.df['total_deduct']
        print("   - 전 사원 계산 완료.")

    def create_visualizations(self):
        """[Step 3] 경영진 보고용 차트 생성"""
        print(">> 3. 데이터 시각화 (그래프 생성)")
        plt.style.use('ggplot')
        
        # 1. 부서별 평균 실수령액
        plt.figure(figsize=(10, 6))
        dept_avg = self.df.groupby('dept')['net_pay'].mean()
        bars = plt.bar(dept_avg.index, dept_avg.values, color='cornflowerblue', edgecolor='black')
        plt.title(f"{self.current_month} 부서별 평균 실수령액", fontsize=15)
        plt.ylabel("금액 (원)")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(f"{self.output_dir}/Chart1_Dept_Avg.png")
        plt.close()
        
        # 2. 급여 구성비 (Stacked Bar)
        plt.figure(figsize=(10, 6))
        plt.bar(self.df['name'], self.df['base_pay'], label='기본급', color='lightgray')
        plt.bar(self.df['name'], self.df['overtime_pay'], bottom=self.df['base_pay'], label='초과수당', color='salmon')
        plt.title("사원별 급여 구성 (기본급 vs 수당)", fontsize=15)
        plt.legend()
        plt.savefig(f"{self.output_dir}/Chart2_Salary_Composition.png")
        plt.close()
        print("   - 그래프 저장 완료.")

    def generate_encrypted_pdfs(self):
        """[Step 4] 암호화된 급여 명세서 생성"""
        print(f">> 4. 보안 PDF 명세서 생성 (총 {len(self.df)}건)")
        
        for _, row in self.df.iterrows():
            filename = f"{self.output_dir}/Payslip_{row['emp_id']}_{row['name']}.pdf"
            
            # 암호 설정: 생년월일 (없으면 사번)
            password = str(row['birth_date'])
            enc = StandardEncryption(password, canPrint=1, canCopy=0, canModify=0)
            
            c = canvas.Canvas(filename, pagesize=A4, encrypt=enc)
            
            # PDF 디자인
            c.setFont(self.font_name, 22)
            c.drawString(50, 800, "급 여 명 세 서")
            
            c.setFont(self.font_name, 10)
            c.drawString(50, 770, f"지급월: {self.current_month} | 성명: {row['name']} ({row['dept']})")
            c.line(50, 760, 545, 760)
            
            y = 730
            c.setFont(self.font_name, 12)
            c.drawString(50, y, "[지급 내역]")
            c.drawString(50, y-25, f"• 기본급: {row['base_pay']:,} 원")
            c.drawString(50, y-50, f"• 초과수당: {row['overtime_pay']:,} 원")
            c.drawString(50, y-75, f"▶ 지급계: {row['total_pay']:,} 원")
            
            c.drawString(300, y, "[공제 내역]")
            c.drawString(300, y-25, f"• 4대보험계: {row['pension']+row['health']+row['care']+row['employ']:,} 원")
            c.drawString(300, y-50, f"• 소득세(지방세포함): {row['income_tax']+row['local_tax']:,} 원")
            c.drawString(300, y-75, f"▶ 공제계: {row['total_deduct']:,} 원")
            
            c.line(50, y-100, 545, y-100)
            c.setFont(self.font_name, 18)
            c.drawString(50, y-130, f"실 수 령 액: {row['net_pay']:,} 원")
            
            c.setFont(self.font_name, 9)
            c.drawString(50, 50, "※ 본 파일은 암호화되어 있습니다. (비밀번호: 생년월일 6자리)")
            
            c.save()

    def export_excel_files(self):
        """[Step 5] 최종 리포트 저장"""
        # 전체 원장
        self.df.to_excel(f"{self.output_dir}/Master_Payroll_Report.xlsx", index=False)
        
        # 은행 이체 리스트
        bank_cols = ['name', 'bank_name', 'account_number', 'net_pay']
        self.df[bank_cols].to_excel(f"{self.output_dir}/Bank_Transfer_List.xlsx", index=False)
        print(">> 5. 엑셀 파일 생성 완료.")

# ==========================================
# [Main] 프로그램 실행부
# ==========================================
if __name__ == "__main__":
    # 1. DB 초기화 (최초 실행 시 데이터 생성)
    db_manager = PayrollDBManager()
    db_manager.initialize_db()
    
    # 2. 워크플로우 실행
    workflow = MasterPayrollWorkflow()
    workflow.load_and_merge_data()     # 병합
    workflow.calculate_payroll()       # 계산
    workflow.create_visualizations()   # 시각화
    workflow.generate_encrypted_pdfs() # 문서화
    workflow.export_excel_files()      # 리포팅
    
    print(f"\n✅ [성공] 모든 작업이 완료되었습니다. '{workflow.output_dir}' 폴더를 확인하세요.")
