#!/bin/bash
LOG_FILE="infrastructure/download_node/recovery_snapshots/status.log"
# 시뮬레이션: 15% 확률로 장애 발생
if [ $((RANDOM % 7)) -eq 0 ]; then
  echo "[Thu Dec 11 12:58:44 UTC 2025] CRITICAL: Connection Refused" >> $LOG_FILE
  exit 1
else
  echo "[Thu Dec 11 12:58:44 UTC 2025] OK: Service Healthy" >> $LOG_FILE
  exit 0
fi
