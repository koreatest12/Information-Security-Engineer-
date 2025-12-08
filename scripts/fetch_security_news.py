import os
import requests
import datetime
import sys

# ==========================================
# 🛡️ Security Resource Configuration
# 정보보안기사 및 보안 실무 필수 공식 리소스
# ==========================================
RESOURCE_MAP = {
    "Exam & Certification": [
        {"name": "CQ (정보보안기사 접수)", "url": "https://www.cq.or.kr"},
        {"name": "KISA Academy (온라인 교육)", "url": "https://academy.kisa.or.kr"}
    ],
    "Domestic Guidelines (KISA)": [
        {"name": "KISA 보호나라 (KrCERT)", "url": "https://www.boho.or.kr"},
        {"name": "KISA 가이드라인 자료실", "url": "https://www.kisa.or.kr/2060204/form?drwCd=CD0000000005"},
        {"name": "ISMS-P 인증 기준", "url": "https://isms.kisa.or.kr/main/isp/issue/law.jsp"},
        {"name": "개인정보보호 포털", "url": "https://www.privacy.go.kr"}
    ],
    "Global Standards (OWASP)": [
        {"name": "OWASP Top 10 (Web)", "url": "https://owasp.org/www-project-top-ten/"},
        {"name": "OWASP API Security Top 10", "url": "https://owasp.org/www-project-api-security/"},
        {"name": "OWASP WSTG (Testing Guide)", "url": "https://owasp.org/www-project-web-security-testing-guide/"}
    ]
}

README_FILE = "README.md"
START_MARKER = ""
END_MARKER = ""

def check_url_status(url):
    """
    User-Agent를 사용하여 봇 차단을 우회하고 사이트 상태를 점검합니다.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # 타임아웃을 10초로 설정하여 무한 대기 방지
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return "✅ Active"
        else:
            return f"⚠️ Status {response.status_code}"
    except requests.exceptions.Timeout:
        return "⏰ Timeout"
    except Exception as e:
        return "❌ Unreachable"

def generate_dashboard_markdown():
    """
    마크다운 대시보드 내용을 생성합니다.
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (KST)")
    
    md_lines = []
    # 마커 사이에 들어갈 내용만 생성 (마커 자체는 제외)
    md_lines.append(f"\n\n## 🧭 Security Resource Dashboard")
    md_lines.append(f"> **Last Updated:** {today}")
    md_lines.append(f"> 정보보안기사 학습 및 실무에 필요한 공식 자료들의 최신 링크 상태입니다.\n")
    
    for category, links in RESOURCE_MAP.items():
        md_lines.append(f"### {category}")
        md_lines.append(f"| Resource Name | Official Link | Status |")
        md_lines.append(f"| :--- | :--- | :--- |")
        
        for link in links:
            print(f"Checking: {link['name']}...") # 로그 출력
            status = check_url_status(link['url'])
            md_lines.append(f"| **{link['name']}** | [Direct Link]({link['url']}) | {status} |")
        md_lines.append("")

    md_lines.append("\n")
    return "\n".join(md_lines)

def update_readme():
    """
    README.md 파일의 내용을 안전하게 업데이트합니다.
    split() 대신 find()와 슬라이싱을 사용하여 안정성을 확보했습니다.
    """
    dashboard_content = generate_dashboard_markdown()
    full_block = f"{START_MARKER}{dashboard_content}{END_MARKER}"
    
    # 1. README 파일이 없으면 생성
    if not os.path.exists(README_FILE):
        print(f"Warning: {README_FILE} not found. Creating a new one.")
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(f"# Information Security Engineer\n\n{full_block}")
        return

    # 2. 파일 읽기
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. 마커 위치 찾기 (find 사용 - 안전함)
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)

    # 4. 내용 교체 로직
    if start_idx != -1 and end_idx != -1:
        print("Updating existing dashboard...")
        # 기존 마커 앞부분 + 새로운 내용 + 기존 마커 뒷부분(END_MARKER 이후)
        # END_MARKER의 길이만큼 더해줘야 마커 뒤부터 자름
        pre_content = content[:start_idx]
        post_content = content[end_idx + len(END_MARKER):]
        new_content = pre_content + full_block + post_content
    else:
        print("Appending new dashboard...")
        # 마커가 없으면 파일 맨 끝에 추가
        new_content = content + "\n\n" + full_block

    # 5. 파일 쓰기
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("SUCCESS: README.md has been successfully updated.")

if __name__ == "__main__":
    print("=== Starting Security Resource Collector ===")
    try:
        update_readme()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
