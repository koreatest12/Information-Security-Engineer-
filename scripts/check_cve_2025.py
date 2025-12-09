import json
import sys
import subprocess
import os
from packaging import version

# 색상 코드
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

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

def get_installed_packages():
    try:
        # 현재 작업 디렉토리 기준
        cwd = os.getcwd()
        # print(f"Scanning in: {cwd}")
        
        result = subprocess.run(
            ["npm", "list", "--json", "--depth=3"], 
            capture_output=True, 
            text=True
        )
        return json.loads(result.stdout)
    except Exception:
        return {}

def find_package_versions(dependencies, target_pkgs, found_list):
    if not dependencies: return
    for pkg_name, pkg_info in dependencies.items():
        if any(target in pkg_name for target in target_pkgs):
            found_list.append({"name": pkg_name, "version": pkg_info.get("version", "0.0.0")})
        if "dependencies" in pkg_info:
            find_package_versions(pkg_info["dependencies"], target_pkgs, found_list)

def is_vulnerable(pkg_name, current_ver_str):
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
    except:
        pass
    return None

def main():
    data = get_installed_packages()
    targets = ["react", "next", "react-server-dom"]
    found_pkgs = []
    
    find_package_versions(data.get("dependencies", {}), targets, found_pkgs)
    
    if not found_pkgs:
        print(f"{YELLOW}   [SKIP] No React/Next.js dependencies found here.{RESET}")
        return # 에러 아님, 그냥 스킵

    vulnerable_detected = False
    checked = set()

    for pkg in found_pkgs:
        uid = f"{pkg['name']}@{pkg['version']}"
        if uid in checked: continue
        checked.add(uid)
        
        patched = is_vulnerable(pkg['name'], pkg['version'])
        if patched:
            print(f"{RED}   ❌ {pkg['name']}@{pkg['version']} -> VULNERABLE (Patch: {patched}){RESET}")
            vulnerable_detected = True
        else:
            print(f"{GREEN}   ✅ {pkg['name']}@{pkg['version']} -> Safe{RESET}")

    if vulnerable_detected:
        print(f"{RED}   🚨 ACTION REQUIRED: Update dependencies in this folder!{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
