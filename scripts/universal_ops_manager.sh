#!/bin/bash
set -euo pipefail

# =======================================================
# ⚙️ GLOBAL CONFIGURATION
# =======================================================
WORKSPACE_DIR="${PWD}"
DATA_DIR="${WORKSPACE_DIR}/data"
CACHE_DIR="${WORKSPACE_DIR}/.cache"
SCRIPTS_DIR="${WORKSPACE_DIR}/scripts"
LOG_FILE="${DATA_DIR}/ops_execution.log"
IMAGE_NAME="grand-ops-image"
IMAGE_TAG="latest"

# 🎨 Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${GREEN}[${timestamp}] [OPS]${NC} $1"
    # Ensure log directory exists before writing
    if [ -d "${DATA_DIR}" ]; then
        echo "[${timestamp}] [OPS] $1" >> "${LOG_FILE}"
    fi
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# =======================================================
# 1️⃣ OS DETECTION & UPGRADE
# =======================================================
detect_and_upgrade_os() {
    log "🔍 Detecting Operating System..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$ID
    else
        OS_NAME="unknown"
    fi

    log "Detected OS: ${OS_NAME}"
    log "🚀 Starting System Upgrade..."

    case "${OS_NAME}" in
        ubuntu|debian)
            sudo apt-get update && sudo apt-get upgrade -y
            sudo apt-get install -y docker.io python3-pip
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                sudo dnf update -y
                sudo dnf install -y docker python3-pip
            else
                sudo yum update -y
                sudo yum install -y docker python3-pip
            fi
            ;;
        alpine)
            apk update && apk upgrade
            apk add docker py3-pip
            ;;
        *)
            log "${YELLOW}⚠️ Unknown OS. Skipping package manager upgrade.${NC}"
            ;;
    esac
    log "✅ System Upgrade Completed."
}

# =======================================================
# 2️⃣ DIRECTORY & PATH SETUP
# =======================================================
setup_environment() {
    log "🛠 Creating Directory Structure..."
    mkdir -p "${DATA_DIR}"
    mkdir -p "${CACHE_DIR}"
    mkdir -p "${SCRIPTS_DIR}"
    
    # Path 설정 (현재 세션용)
    export PATH="${SCRIPTS_DIR}:${PATH}"
    
    # Cache 파일 생성 (예시)
    touch "${CACHE_DIR}/ops_cache_$(date +%Y%m%d).dat"
    
    log "✅ Directories created: ${DATA_DIR}, ${CACHE_DIR}, ${SCRIPTS_DIR}"
    log "✅ PATH updated."
}

# =======================================================
# 3️⃣ IMAGE BUILD (Docker)
# =======================================================
build_image() {
    log "🐳 Checking for Dockerfile..."
    if [ -f "Dockerfile" ]; then
        log "🚀 Building Docker Image: ${IMAGE_NAME}:${IMAGE_TAG}"
        if sudo docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .; then
            log "✅ Image Build Success."
        else
            error "Image Build Failed."
        fi
    else
        log "${YELLOW}⚠️ No Dockerfile found. Skipping build step.${NC}"
    fi
}

# =======================================================
# 4️⃣ EXECUTE SCRIPTS (Recursive)
# =======================================================
run_scripts() {
    log "📜 Scanning for scripts in ${SCRIPTS_DIR}..."
    
    # 스크립트 디렉토리가 비어있지 않은지 확인
    if [ -z "$(ls -A ${SCRIPTS_DIR})" ]; then
        log "ℹ️ No scripts found to execute."
        return
    fi

    for script in "${SCRIPTS_DIR}"/*; do
        if [ -f "$script" ]; then
            filename=$(basename "$script")
            extension="${filename##*.}"
            
            log "▶️ Executing: $filename"
            
            case "$extension" in
                sh)
                    chmod +x "$script"
                    bash "$script" || log "${RED}❌ Script failed: $filename${NC}"
                    ;;
                py)
                    python3 "$script" || log "${RED}❌ Script failed: $filename${NC}"
                    ;;
                *)
                    log "ℹ️ Skipping non-executable file: $filename"
                    ;;
            esac
        fi
    done
    log "✅ Script execution batch finished."
}

# =======================================================
# 🚀 MAIN EXECUTION FLOW
# =======================================================
main() {
    echo "=========================================="
    echo "   GRAND OPS: UNIVERSAL MANAGER v2.0      "
    echo "=========================================="
    
    detect_and_upgrade_os
    setup_environment
    build_image
    run_scripts
    
    log "🎉 All Operations Completed Successfully."
}

main
