import json, os
# 샘플 보안 뉴스 데이터 생성
data = [
    {"id": 1, "title": "CVE-2026-0001 분석", "severity": "High"},
    {"id": 2, "title": "Shadow File Integrity Check", "severity": "Critical"}
]
os.makedirs('data', exist_ok=True)
with open('data/daily_intel.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
