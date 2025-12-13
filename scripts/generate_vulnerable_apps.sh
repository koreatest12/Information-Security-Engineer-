#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Generating Vulnerable Test Environments...${NC}"

# 1. 루트 레벨 취약점 (Next.js 15.0.0 - 취약함)
echo "1️⃣ Creating root-level vulnerable package.json..."
cat <<EOF > package.json
{
  "name": "root-vulnerable-app",
  "version": "1.0.0",
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0"
  }
}
EOF

# 2. 하위 폴더 (backend) 취약점 (React 19.0.0 - 취약함)
mkdir -p backend
echo "2️⃣ Creating backend/package.json (Vulnerable React)..."
cat <<EOF > backend/package.json
{
  "name": "backend-service",
  "version": "0.1.0",
  "dependencies": {
    "express": "^4.17.1",
    "react": "19.0.0",
    "react-server-dom-webpack": "19.0.0"
  }
}
EOF

# 3. 깊은 폴더 (services/frontend) - (Safe 버전 - 비교용)
mkdir -p services/frontend
echo "3️⃣ Creating services/frontend/package.json (Safe Version)..."
cat <<EOF > services/frontend/package.json
{
  "name": "safe-frontend",
  "version": "2.0.0",
  "dependencies": {
    "next": "15.0.5",
    "react": "19.0.1",
    "react-dom": "19.0.1"
  }
}
EOF

echo -e "${GREEN}✅ All test files generated successfully!${NC}"
echo -e "${RED}⚠️ NOTE: Do not deploy these files to production. They contain critical vulnerabilities.${NC}"
