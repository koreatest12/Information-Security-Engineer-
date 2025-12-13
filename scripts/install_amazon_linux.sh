#!/bin/bash

##############################################
# Amazon Linux 2/2023 설치 및 업그레이드 스크립트
# Node.js, Python, Java, MySQL, PostgreSQL, MongoDB
##############################################

set -e  # 에러 발생 시 스크립트 중단

echo "========================================"
echo "Amazon Linux 환경 설정 시작"
echo "========================================"

# 시스템 업데이트
echo "시스템 패키지 업데이트 중..."
sudo yum update -y

# 필수 도구 설치
echo "필수 도구 설치 중..."
sudo yum install -y curl wget git gcc gcc-c++ make openssl-devel bzip2-devel libffi-devel zlib-devel tar

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

# Amazon Linux 2023은 Python 3.11을 기본 제공
# Amazon Linux 2는 소스 컴파일 필요

AL_VERSION=$(cat /etc/system-release | grep -o "Amazon Linux [0-9]*" | awk '{print $3}')

if [ "$AL_VERSION" == "2023" ]; then
    echo "Amazon Linux 2023 감지 - yum으로 설치"
    sudo yum install -y python3.11 python3.11-pip python3.11-devel
else
    echo "Amazon Linux 2 감지 - 소스 컴파일"
    # Python 3.11 소스 다운로드 및 컴파일
    cd /tmp
    wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
    tar xzf Python-3.11.7.tgz
    cd Python-3.11.7
    
    # 컴파일 및 설치
    ./configure --enable-optimizations --with-ssl
    sudo make altinstall
    
    # 정리
    cd ~
    rm -rf /tmp/Python-3.11.7*
fi

# pip 업그레이드
sudo python3.11 -m pip install --upgrade pip

# 버전 확인
echo "Python 버전:"
python3.11 --version
echo "pip 버전:"
python3.11 -m pip --version

##############################################
# Java 설치 (Amazon Corretto 17)
##############################################
echo "========================================"
echo "Java 설치 중..."
echo "========================================"

# Amazon Corretto 17 설치 (AWS 최적화 OpenJDK)
sudo yum install -y java-17-amazon-corretto-devel

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

AL_VERSION=$(cat /etc/system-release | grep -o "Amazon Linux [0-9]*" | awk '{print $3}')

if [ "$AL_VERSION" == "2023" ]; then
    # Amazon Linux 2023
    sudo yum install -y https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm
else
    # Amazon Linux 2
    sudo yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-1.noarch.rpm
fi

# MySQL GPG 키 임포트
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2023

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

AL_VERSION=$(cat /etc/system-release | grep -o "Amazon Linux [0-9]*" | awk '{print $3}')

if [ "$AL_VERSION" == "2023" ]; then
    # Amazon Linux 2023
    sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
else
    # Amazon Linux 2
    sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
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

AL_VERSION=$(cat /etc/system-release | grep -o "Amazon Linux [0-9]*" | awk '{print $3}')

if [ "$AL_VERSION" == "2023" ]; then
    # MongoDB 저장소 추가 (AL2023)
    cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc
EOF
else
    # MongoDB 저장소 추가 (AL2)
    cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc
EOF
fi

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
