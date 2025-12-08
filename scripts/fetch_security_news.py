import os
import requests
import datetime
import sys

RESOURCE_MAP = {
    "Exam & Certification": [
        {"name": "CQ (정보보안기사)", "url": "https://www.cq.or.kr"},
        {"name": "KISA Academy", "url": "https://academy.kisa.or.kr"}
    ],
    "Domestic Guidelines (KISA)": [
        {"name": "KISA KrCERT", "url": "https://www.boho.or.kr"},
        {"name": "KISA Guidelines", "url": "https://www.kisa.or.kr/2060204/form?drwCd=CD0000000005"},
        {"name": "ISMS-P Criteria", "url": "https://isms.kisa.or.kr/main/isp/issue/law.jsp"}
    ],
    "Global Standards (OWASP)": [
        {"name": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/"},
        {"name": "OWASP WSTG", "url": "https://owasp.org/www-project-web-security-testing-guide/"}
    ]
}

README_FILE = "README.md"
# [FIX] 마커가 비어있으면 동작하지 않으므로 HTML 주석을 정확히 명시
START_MARKER = ""
END_MARKER = ""

def check_url_status(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return "✅ Active" if response.status_code == 200 else f"⚠️ {response.status_code}"
    except:
        return "❌ Unreachable"

def update_readme():
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (KST)")
    md = [f"\n\n## 🧭 Security Resource Dashboard", f"> **Last Updated:** {today}\n"]
    
    for cat, links in RESOURCE_MAP.items():
        md.append(f"### {cat}\n| Name | Link | Status |\n|---|---|---|")
        for link in links:
            status = check_url_status(link['url'])
            md.append(f"| **{link['name']}** | [Link]({link['url']}) | {status} |")
        md.append("")
    
    dashboard = "\n".join(md)
    full_block = f"{START_MARKER}{dashboard}{END_MARKER}"

    if not os.path.exists(README_FILE):
        with open(README_FILE, "w", encoding="utf-8") as f: f.write(f"# InfoSec\n{full_block}")
        return

    with open(README_FILE, "r", encoding="utf-8") as f: content = f.read()
    
    # find() 안전한 사용
    s_idx = content.find(START_MARKER)
    e_idx = content.find(END_MARKER)
    
    if s_idx != -1 and e_idx != -1:
        # 기존 대시보드 교체
        new_content = content[:s_idx] + full_block + content[e_idx + len(END_MARKER):]
    else:
        # 없으면 끝에 추가
        new_content = content + "\n\n" + full_block
    
    with open(README_FILE, "w", encoding="utf-8") as f: f.write(new_content)

if __name__ == "__main__":
    update_readme()
