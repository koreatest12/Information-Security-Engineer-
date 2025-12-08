import os
import requests
import datetime

# 자료 저장 경로
SAVE_DIR = "materials"
README_FILE = "README.md"

# 다운로드할 공식 자료 목록 (URL 및 파일명)
# 실제 운영 시, KISA 자료실의 게시판 ID를 파싱하는 로직으로 확장 가능
TARGET_RESOURCES = [
    {
        "source": "OWASP",
        "title": "OWASP Top 10 (2021) PDF",
        "url": "https://owasp.org/www-project-top-ten/assets/images/mapping.png", # 예시: 실제 PDF 링크로 교체 권장
        "filename": "OWASP_Top_10_Map.png"
    },
    {
        "source": "KISA",
        "title": "KISA 랜섬웨어 대응 가이드",
        "url": "https://www.kisa.or.kr", # KISA는 동적 링크를 사용하므로 메인 페이지를 참조하거나 특정 고정 링크 필요
        "filename": "KISA_Ransomware_Guide_Placeholder.html" 
    }
]

def download_file(url, filename):
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    
    filepath = os.path.join(SAVE_DIR, filename)
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True, filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False, None

def update_readme(downloaded_items):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    new_content = f"\n\n### 📥 Auto-Collected Materials ({today})\n"
    for item in downloaded_items:
        new_content += f"- **[{item['source']}]** {item['title']} (Saved to: `{item['path']}`)\n"
    
    # README.md 파일 끝에 내용 추가
    with open(README_FILE, "a", encoding="utf-8") as f:
        f.write(new_content)

def main():
    print("Starting Security Material Collection...")
    downloaded = []
    
    for resource in TARGET_RESOURCES:
        print(f"Fetching: {resource['title']}...")
        success, path = download_file(resource['url'], resource['filename'])
        if success:
            downloaded.append({
                "source": resource['source'],
                "title": resource['title'],
                "path": path
            })
    
    if downloaded:
        print(f"Downloaded {len(downloaded)} items. Updating README...")
        update_readme(downloaded)
    else:
        print("No items downloaded.")

if __name__ == "__main__":
    main()
