import json
import sys
import subprocess
from packaging import version

# --- 취약점 데이터베이스 (프롬프트 기반) ---
VULNERABLE_RANGES = {
    "react": [
        {"start": "19.0.0", "end": "19.0.0", "patched": "19.0.1"},
        {"start": "19.1.0", "end": "19.1.1", "patched": "19.1.2"},
        {"start": "19.2.0", "end": "19.2.0", "patched": "19.2.1"},
    ],
    "react-server-dom-webpack": [ # react-server-dom* 계열 포괄
        {"start": "19.0.0", "end": "19.2.0", "patched": "Check React Version"}
    ],
    "next": [
        {"start": "14.3.0-canary.0", "end": "14.3.0-canary.87", "patched": "14.3.0-canary.88"},
        {"start": "15.0.0", "end": "15.0.4", "patched": "15.0.5"},
        {"start": "15.1.0", "end": "15.1.8", "patched": "15.1.9"},
        {"start": "15.2.0", "end": "15.2.5", "patched": "15.2.6"},
        {"start": "15.3.0", "end": "15.3.5", "patched": "15.3.6"},
        {"start": "15.4.0", "end": "15.4.7", "patched": "15.4.8"},
        {"start": "15.5.0", "end": "15.5.6", "patched": "15.5.7"},
        {"start": "16.0.0", "end": "16.0.6", "patched": "16.0.7"},
    ]
}

def get_installed_packages():
    """npm list --json을 통해 설치된 모든 패키지 트리 확보"""
    try:
        # depth=3 정도로 제한하여 성능 확보 (필요시 조정)
        result = subprocess.run(
            ["npm", "list", "--json", "--depth=3"], 
            capture_output=True, 
            text=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running npm list: {e}")
        sys.exit(1)

def find_package_versions(dependencies, target_pkgs, found_list):
    """재귀적으로 의존성 트리를 탐색"""
    if not dependencies:
        return

    for pkg_name, pkg_info in dependencies.items():
        # 패키지명이 타겟(react, next 등)과 일치하거나 포함되는지 확인
        if any(target in pkg_name for target in target_pkgs):
            found_list.append({
                "name": pkg_name,
                "version": pkg_info.get("version", "0.0.0")
            })
        
        if "dependencies" in pkg_info:
            find_package_versions(pkg_info["dependencies"], target_pkgs, found_list)

def is_vulnerable(pkg_name, current_ver_str):
    """현재 버전이 취약한 범위에 있는지 확인"""
    try:
        current_ver = version.parse(current_ver_str)
        
        # 패키지 이름 매칭 (react, next 등)
        key = "next" if "next" in pkg_name else "react"
        if "react-server-dom" in pkg_name: key = "react-server-dom-webpack"

        ranges = VULNERABLE_RANGES.get(key, [])
        
        for rule in ranges:
            start = version.parse(rule["start"])
            end = version.parse(rule["end"])
            
            # 범위 체크: start <= current <= end
            if start <= current_ver <= end:
                return rule["patched"]
                
    except Exception:
        # 파싱 불가능한 버전(로컬 경로 등)은 스킵
        pass
    return None

def main():
    print("🔍 Starting CVE-2025-55182 & CVE-2025-66478 Vulnerability Scan...")
    
    data = get_installed_packages()
    targets = ["react", "next", "react-server-dom"]
    found_pkgs = []
    
    find_package_versions(data.get("dependencies", {}), targets, found_pkgs)
    
    vulnerable_detected = False
    
    print(f"{'-'*60}")
    print(f"{'Package':<30} | {'Current':<15} | {'Status'}")
    print(f"{'-'*60}")

    checked_cache = set()

    for pkg in found_pkgs:
        uid = f"{pkg['name']}@{pkg['version']}"
        if uid in checked_cache: continue
        checked_cache.add(uid)

        patched_ver = is_vulnerable(pkg['name'], pkg['version'])
        
        if patched_ver:
            print(f"❌ {pkg['name']:<27} | {pkg['version']:<15} | 🚨 VULNERABLE (Update to {patched_ver})")
            vulnerable_detected = True
        else:
            print(f"✅ {pkg['name']:<27} | {pkg['version']:<15} | Safe")

    print(f"{'-'*60}")

    if vulnerable_detected:
        print("\n🚨 CRITICAL: Vulnerable versions detected! Please update immediately.")
        sys.exit(1) # CI 파이프라인 실패 처리
    else:
        print("\n✅ System is secure against specified CVEs.")
        sys.exit(0)

if __name__ == "__main__":
    main()
