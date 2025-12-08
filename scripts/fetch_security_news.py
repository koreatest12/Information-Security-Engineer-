import os
import requests
import datetime
import sys

# ==========================================
# 🛡️ Security Resource Configuration
# 정보보안기사 공부에 필수적인 공식 리소스 목록
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

def check_url_status(url):
    """
    각 사이트가 정상적으로 동작하는지 상태 코드를 확인합니다.
    User-Agent 헤더를 사용하여 봇 차단을 방지합니다.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return "✅ Active"
        else:
            return f"⚠️ Status {response.status_code}"
    except Exception:
        return "❌ Unreachable"

def generate_dashboard_markdown():
    """
    리소스 맵을 기반으로 마크다운 대시보드 내용을 생성합니다.
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (KST)")
    
    md_lines = []
    md_lines.append(f"\n\n## 🧭 Security Resource Dashboard")
    md_lines.append(f"> **Last Updated:** {today}")
    md_lines.append(f"> 정보보안기사 학습에 필요한 공식 자료들의 최신 링크와 상태입니다.\n")
    
    for category, links in RESOURCE_MAP.items():
        md_lines.append(f"### {category}")
        md_lines.append(f"| Resource Name | Official Link | Status |")
        md_lines.append(f"| :--- | :--- | :--- |")
        
        for link in links:
            status = check_url_status(link['url'])
            md_lines.append(f"| **{link['name']}** | [Direct Link]({link['url']}) | {status} |")
        md_lines.append("") # Empty line for spacing

    md_lines.append("\n---\n")
    return "\n".join(md_lines)

def update_readme():
    """
    README.md 파일을 읽어서 기존 대시보드가 있다면 교체하고,
    없다면 하단에 새로 추가합니다.
    """
    dashboard_content = generate_dashboard_markdown()
    
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found.")
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존에 대시보드 섹션이 있는지 확인 (마커 사용)
    start_marker = ""
    end_marker = ""

    if start_marker in content and end_marker in content:
        # 기존 내용 교체 (Regex 없이 문자열 슬라이싱으로 안전하게 처리)
        pre_content = content.split(start_marker)[0]
        post_content = content.split(end_marker)[1]
        new_content = f"{pre_content}{start_marker}{dashboard_content}{end_marker}{post_content}"
    else:
        # 파일 끝에 추가
        new_content = f"{content}\n\n{start_marker}{dashboard_content}{end_marker}"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("README.md has been successfully updated with the Security Dashboard.")

if __name__ == "__main__":
    print("Starting Security Resource Check...")
    update_readme()
