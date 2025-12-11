#!/bin/bash

SERVICE_NAME=$1
VERSION=$2
TYPE=$3 # (app, db, security)

BASE_DIR="servers/$TYPE/$SERVICE_NAME"
BACKUP_DIR="backups/$SERVICE_NAME/$(date +%Y%m%d_%H%M%S)"

echo "--------------------------------------------------"
echo "🔧 Process Initiated: $SERVICE_NAME (Target: v$VERSION)"

# 1. 업그레이드 감지 및 백업 (Upgrade & Backup)
if [ -d "$BASE_DIR" ]; then
  echo "⚠️  Existing installation detected. Starting Backup..."
  mkdir -p $BACKUP_DIR
  cp -r $BASE_DIR/* $BACKUP_DIR/
  echo "✅ Backup Secure: $BACKUP_DIR"
  echo "🔄 Upgrading from existing version to v$VERSION..."
else
  echo "🆕 New Installation Mode Activated."
fi

# 2. 표준 디렉토리 구조 생성 (Standard Directory Provisioning)
mkdir -p $BASE_DIR/bin
mkdir -p $BASE_DIR/conf
mkdir -p $BASE_DIR/logs
mkdir -p $BASE_DIR/data

# 3. 바이너리 및 설정 파일 설치 (Simulation)
echo "Binary Data for $SERVICE_NAME v$VERSION" > $BASE_DIR/bin/$SERVICE_NAME.bin
echo "Config Standard v$VERSION" > $BASE_DIR/conf/$SERVICE_NAME.conf
echo "Installation Date: $(date)" > $BASE_DIR/install_receipt.txt

# 4. 매니페스트 업데이트 (Inventory Update)
echo "{\"$SERVICE_NAME\": \"$VERSION\"}" >> inventory/server_manifest.json

echo "✨ $SERVICE_NAME v$VERSION Installation/Upgrade Complete."
echo "--------------------------------------------------"
