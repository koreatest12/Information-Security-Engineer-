import json
import sys
import subprocess
import os
from packaging import version

# --- 색상 코드 (가독성 향상) ---
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# --- 취약점 데이터베이스 ---
VULNERABLE_RANGES = {
    "react": [
        {"start": "19.0.0", "end": "19.0.0", "patched": "19.0.1"},
        {"start": "19.1.0", "end": "19.1.1", "patched": "19.1.2"},
        {"start": "19.2.0", "end": "19.2.0", "patched": "19.2.1"},
    ],
    "react-server-dom-webpack": [
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

def check_requirements():
    """패키지 매니저 및 필수 파일 확인"""
    if not os.path.exists("package.json"):
        print(f"{YELLOW}[WARN] No package.json found. Skipping scan.{RESET}")
        sys.exit(0) # 에러 아님, 스캔 할 게 없을 뿐

def get_installed_packages():
    """npm list --json을 통해 설치된 모든 패키지 트리 확보"""
    print(f"📦 Extracting dependency tree...")
    try:
        # depth=5로 늘려 더 깊은 의존성까지 확인
        result = subprocess.run(
            ["npm", "list", "--json", "--depth=5"], 
            capture_output=True, 
            text=True
        )
        # npm list가 실패해도(peer dep 에러 등) JSON은 출력될 수 있음
        if not result.stdout.strip():
            print(f"{RED}[ERR] Failed to get npm list output.{RESET}")
            sys.exit(1)
            
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"{RED}[ERR] Failed to parse npm list output. Ensure dependencies are installed.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}[ERR] Unexpected error: {e}{RESET}")
        sys.exit(1)

def find_package_versions(dependencies, target_pkgs, found_list):
    """재귀적으로 의존성 트리를 탐색"""
    if not dependencies:
        return

    for pkg_name, pkg_info in dependencies.items():
        if any(target in pkg_name for target in target_pkgs):
            found_list.append({
                "name": pkg_name,
                "version": pkg_info.get("version", "0.0.0")
            })
        
        if "dependencies" in pkg_info:
            find_package_versions(pkg_info["dependencies"], target_pkgs, found_list)

def is_vulnerable(pkg_name, current_ver_str):
    """버전 비교 로직"""
    try:
        current_ver = version.parse(current_ver_str)
        
        key = "next" if "next" in pkg_name else "react"
        if "react-server-dom" in pkg_name: key = "react-server-dom-webpack"

        ranges = VULNERABLE_RANGES.get(key, [])
        
        for rule in ranges:
            start = version.parse(rule["start"])
            end = version.parse(rule["end"])
            if start <= current_ver <= end:
                return rule["patched"]
    except Exception:
        pass
    return None

def main():
    print(f"{'='*60}")
    print(f"🔍 CVE-2025-55182 & CVE-2025-66478 Vulnerability Scan")
    print(f"{'='*60}")
    
    check_requirements()
    data = get_installed_packages()
    
    targets = ["react", "next", "react-server-dom"]
    found_pkgs = []
    
    find_package_versions(data.get("dependencies", {}), targets, found_pkgs)
    
    if not found_pkgs:
        print(f"{GREEN}✅ No React or Next.js packages found in this project.{RESET}")
        sys.exit(0)

    vulnerable_detected = False
    checked_cache = set()

    print(f"\n{'-'*75}")
    print(f"{'Package':<35} | {'Current':<15} | {'Status'}")
    print(f"{'-'*75}")

    for pkg in found_pkgs:
        uid = f"{pkg['name']}@{pkg['version']}"
        if uid in checked_cache: continue
        checked_cache.add(uid)

        patched_ver = is_vulnerable(pkg['name'], pkg['version'])
        
        if patched_ver:
            print(f"{RED}❌ {pkg['name']:<32} | {pkg['version']:<15} | 🚨 UPDATE TO {patched_ver}{RESET}")
            vulnerable_detected = True
        else:
            print(f"{GREEN}✅ {pkg['name']:<32} | {pkg['version']:<15} | Safe{RESET}")

    print(f"{'-'*75}")

    if vulnerable_detected:
        print(f"\n{RED}🚨 CRITICAL FAILURE: Vulnerable versions detected!{RESET}")
        print(f"{RED}   Please check package.json or use 'npm audit fix'.{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}✅ System is secure against specified CVEs.{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
