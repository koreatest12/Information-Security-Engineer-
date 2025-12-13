#!/bin/bash

##############################################
# CentOS/RHEL 설치 및 업그레이드 스크립트
# Node.js, Python, Java, MySQL, PostgreSQL, MongoDB
##############################################

set -e  # 에러 발생 시 스크립트 중단

echo "========================================"
echo "CentOS/RHEL 환경 설정 시작"
echo "========================================"

# 시스템 업데이트
echo "시스템 패키지 업데이트 중..."
sudo yum update -y

# EPEL 저장소 설치
echo "EPEL 저장소 설치 중..."
sudo yum install -y epel-release

# 필수 도구 설치
echo "필수 도구 설치 중..."
sudo yum install -y curl wget git gcc gcc-c++ make openssl-devel bzip2-devel libffi-devel zlib-devel

##############################################
# Node.js 설치 (LTS 버전)
##############################################
echo "========================================"
echo "Node.js 설치 중..."
echo "========================================"

# NodeSource 저장소 추가
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -

# Node.js 설치
sudo yum install -y nodejs

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

# Python 3.11 소스 다운로드 및 컴파일
cd /tmp
wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
tar xzf Python-3.11.7.tgz
cd Python-3.11.7

# 컴파일 및 설치
./configure --enable-optimizations --with-ssl
sudo make altinstall  # altinstall을 사용하여 기본 python3를 덮어쓰지 않음

# pip 업그레이드
sudo /usr/local/bin/python3.11 -m pip install --upgrade pip

# 심볼릭 링크 생성 (선택사항)
sudo ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3

# 버전 확인
echo "Python 버전:"
python3.11 --version
echo "pip 버전:"
python3.11 -m pip --version

# 정리
cd ~
rm -rf /tmp/Python-3.11.7*

##############################################
# Java 설치 (OpenJDK 17)
##############################################
echo "========================================"
echo "Java 설치 중..."
echo "========================================"

# OpenJDK 17 설치
sudo yum install -y java-17-openjdk java-17-openjdk-devel

# JAVA_HOME 환경변수 설정
JAVA_PATH=$(dirname $(dirname $(readlink -f $(which java))))
echo "export JAVA_HOME=$JAVA_PATH" | sudo tee -a /etc/profile.d/java.sh
echo "export PATH=\$PATH:\$JAVA_HOME/bin" | sudo tee -a /etc/profile.d/java.sh
source /etc/profile.d/java.sh

# 버전 확인
echo "Java 버전:"
java -version
javac -version

##############################################
# MySQL 설치 (MySQL 8.0)
##############################################
echo "========================================"
echo "MySQL 설치 중..."
echo "========================================"

# MySQL 저장소 추가
sudo yum install -y https://dev.mysql.com/get/mysql80-community-release-el$(rpm -E %{rhel})-1.noarch.rpm

# MySQL 설치
sudo yum install -y mysql-community-server

# MySQL 서비스 시작 및 활성화
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 임시 root 비밀번호 찾기
echo "MySQL 임시 root 비밀번호:"
sudo grep 'temporary password' /var/log/mysqld.log | tail -1

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
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-$(rpm -E %{rhel})-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# 기본 PostgreSQL 모듈 비활성화 (CentOS 8/RHEL 8 이상)
if [ $(rpm -E %{rhel}) -ge 8 ]; then
    sudo dnf -qy module disable postgresql
fi

# PostgreSQL 16 설치
sudo yum install -y postgresql16-server postgresql16

# PostgreSQL 초기화
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb

# PostgreSQL 서비스 시작 및 활성화
sudo systemctl start postgresql-16
sudo systemctl enable postgresql-16

# 버전 확인
echo "PostgreSQL 버전:"
/usr/pgsql-16/bin/psql --version

echo "PostgreSQL 설치 완료. 사용자 설정을 위해 다음을 실행하세요:"
echo "sudo -u postgres /usr/pgsql-16/bin/psql"

##############################################
# MongoDB 설치 (최신 버전)
##############################################
echo "========================================"
echo "MongoDB 설치 중..."
echo "========================================"

# MongoDB 저장소 추가
cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc
EOF

# MongoDB 설치
sudo yum install -y mongodb-org

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
echo "PostgreSQL: $(/usr/pgsql-16/bin/psql --version)"
echo "MongoDB: $(mongod --version | head -n 1)"
echo "----------------------------------------"
echo ""
echo "서비스 상태:"
echo "MySQL: $(sudo systemctl is-active mysqld)"
echo "PostgreSQL: $(sudo systemctl is-active postgresql-16)"
echo "MongoDB: $(sudo systemctl is-active mongod)"
echo ""
echo "추가 보안 설정이 필요합니다:"
echo "1. MySQL: sudo mysql_secure_installation"
echo "2. PostgreSQL: sudo -u postgres /usr/pgsql-16/bin/psql"
echo "3. MongoDB: 인증 활성화 권장"
echo ""
echo "MySQL 임시 root 비밀번호를 확인하세요:"
echo "sudo grep 'temporary password' /var/log/mysqld.log | tail -1"
