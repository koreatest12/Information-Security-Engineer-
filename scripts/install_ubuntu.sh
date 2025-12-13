#!/bin/bash

##############################################
# Ubuntu/Debian 설치 및 업그레이드 스크립트
# Node.js, Python, Java, MySQL, PostgreSQL, MongoDB
##############################################

set -e  # 에러 발생 시 스크립트 중단

echo "========================================"
echo "Ubuntu/Debian 환경 설정 시작"
echo "========================================"

# 시스템 업데이트
echo "시스템 패키지 업데이트 중..."
sudo apt update
sudo apt upgrade -y

# 필수 도구 설치
echo "필수 도구 설치 중..."
sudo apt install -y curl wget git build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release

##############################################
# Node.js 설치 (LTS 버전)
##############################################
echo "========================================"
echo "Node.js 설치 중..."
echo "========================================"

# NodeSource 저장소 추가
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

# Node.js 설치
sudo apt install -y nodejs

# 버전 확인
echo "Node.js 버전:"
node --version
echo "npm 버전:"
npm --version

# npm 글로벌 패키지 업데이트
sudo npm install -g npm@latest

##############################################
# Python 설치 (Python 3.11)
##############################################
echo "========================================"
echo "Python 설치 중..."
echo "========================================"

# Python 저장소 추가
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# Python 3.11 및 관련 패키지 설치
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# pip 업그레이드
python3.11 -m pip install --upgrade pip

# 심볼릭 링크 생성 (선택사항)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 버전 확인
echo "Python 버전:"
python3.11 --version
echo "pip 버전:"
python3.11 -m pip --version

##############################################
# Java 설치 (OpenJDK 17)
##############################################
echo "========================================"
echo "Java 설치 중..."
echo "========================================"

# OpenJDK 17 설치
sudo apt install -y openjdk-17-jdk openjdk-17-jre

# JAVA_HOME 환경변수 설정
echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" | sudo tee -a /etc/profile.d/java.sh
echo "export PATH=\$PATH:\$JAVA_HOME/bin" | sudo tee -a /etc/profile.d/java.sh
source /etc/profile.d/java.sh

# 버전 확인
echo "Java 버전:"
java -version
javac -version

##############################################
# MySQL 설치
##############################################
echo "========================================"
echo "MySQL 설치 중..."
echo "========================================"

sudo apt install -y mysql-server mysql-client

# MySQL 서비스 시작 및 활성화
sudo systemctl start mysql
sudo systemctl enable mysql

echo "MySQL 설치 완료. 보안 설정을 위해 다음 명령어를 실행하세요:"
echo "sudo mysql_secure_installation"

# 버전 확인
echo "MySQL 버전:"
mysql --version

##############################################
# PostgreSQL 설치 (최신 버전)
##############################################
echo "========================================"
echo "PostgreSQL 설치 중..."
echo "========================================"

# PostgreSQL 저장소 추가
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update

# PostgreSQL 설치
sudo apt install -y postgresql postgresql-contrib

# PostgreSQL 서비스 시작 및 활성화
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 버전 확인
echo "PostgreSQL 버전:"
psql --version

echo "PostgreSQL 설치 완료. 사용자 설정을 위해 다음을 실행하세요:"
echo "sudo -u postgres psql"

##############################################
# MongoDB 설치 (최신 버전)
##############################################
echo "========================================"
echo "MongoDB 설치 중..."
echo "========================================"

# MongoDB GPG 키 추가
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# MongoDB 저장소 추가
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update

# MongoDB 설치
sudo apt install -y mongodb-org

# MongoDB 서비스 시작 및 활성화
sudo systemctl start mongod
sudo systemctl enable mongod

# 버전 확인
echo "MongoDB 버전:"
mongod --version

##############################################
# 설치 완료 및 요약
##############################################
echo "========================================"
echo "설치 완료!"
echo "========================================"
echo ""
echo "설치된 버전 정보:"
echo "----------------------------------------"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3.11 --version)"
echo "pip: $(python3.11 -m pip --version)"
echo "Java: $(java -version 2>&1 | head -n 1)"
echo "MySQL: $(mysql --version)"
echo "PostgreSQL: $(psql --version)"
echo "MongoDB: $(mongod --version | head -n 1)"
echo "----------------------------------------"
echo ""
echo "서비스 상태:"
echo "MySQL: $(sudo systemctl is-active mysql)"
echo "PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "MongoDB: $(sudo systemctl is-active mongod)"
echo ""
echo "추가 보안 설정이 필요합니다:"
echo "1. MySQL: sudo mysql_secure_installation"
echo "2. PostgreSQL: sudo -u postgres psql"
echo "3. MongoDB: 인증 활성화 권장"
