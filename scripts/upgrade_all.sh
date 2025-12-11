#!/bin/bash

##############################################
# 통합 업그레이드 스크립트
# 기존 설치된 패키지들을 최신 버전으로 업그레이드
# Ubuntu/Debian, CentOS/RHEL, Amazon Linux 지원
##############################################

set -e  # 에러 발생 시 스크립트 중단

# 운영체제 감지
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
    else
        OS=$(uname -s)
    fi
    
    echo "$OS"
}

OS=$(detect_os)
echo "========================================"
echo "감지된 운영체제: $OS"
echo "통합 업그레이드 시작"
echo "========================================"

##############################################
# 시스템 업데이트
##############################################
echo "시스템 패키지 업데이트 중..."
case $OS in
    ubuntu|debian)
        sudo apt update
        sudo apt upgrade -y
        ;;
    centos|rhel|fedora|amzn)
        sudo yum update -y
        ;;
    *)
        echo "지원하지 않는 운영체제입니다: $OS"
        exit 1
        ;;
esac

##############################################
# Node.js 업그레이드
##############################################
echo "========================================"
echo "Node.js 업그레이드 중..."
echo "========================================"

if command -v node &> /dev/null; then
    echo "현재 Node.js 버전: $(node --version)"
    
    case $OS in
        ubuntu|debian)
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt install -y nodejs
            ;;
        centos|rhel|fedora|amzn)
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
            sudo yum install -y nodejs
            ;;
    esac
    
    # npm 업그레이드
    sudo npm install -g npm@latest
    
    echo "업그레이드된 Node.js 버전: $(node --version)"
    echo "업그레이드된 npm 버전: $(npm --version)"
else
    echo "Node.js가 설치되어 있지 않습니다."
fi

##############################################
# Python pip 패키지 업그레이드
##############################################
echo "========================================"
echo "Python pip 업그레이드 중..."
echo "========================================"

if command -v python3.11 &> /dev/null; then
    echo "현재 Python 버전: $(python3.11 --version)"
    echo "현재 pip 버전: $(python3.11 -m pip --version)"
    
    # pip 업그레이드
    python3.11 -m pip install --upgrade pip
    
    # 주요 패키지 업그레이드
    python3.11 -m pip install --upgrade setuptools wheel virtualenv
    
    echo "pip 업그레이드 완료: $(python3.11 -m pip --version)"
elif command -v python3 &> /dev/null; then
    echo "python3.11이 없습니다. 기본 python3 사용"
    python3 -m pip install --upgrade pip
else
    echo "Python이 설치되어 있지 않습니다."
fi

##############################################
# Java 업그레이드 확인
##############################################
echo "========================================"
echo "Java 확인 중..."
echo "========================================"

if command -v java &> /dev/null; then
    echo "현재 Java 버전:"
    java -version
    
    case $OS in
        ubuntu|debian)
            echo "OpenJDK 업그레이드 확인 중..."
            sudo apt install -y --only-upgrade openjdk-17-jdk openjdk-17-jre
            ;;
        centos|rhel|fedora)
            echo "OpenJDK 업그레이드 확인 중..."
            sudo yum update -y java-17-openjdk java-17-openjdk-devel
            ;;
        amzn)
            echo "Amazon Corretto 업그레이드 확인 중..."
            sudo yum update -y java-17-amazon-corretto-devel
            ;;
    esac
    
    echo "업그레이드 후 Java 버전:"
    java -version
else
    echo "Java가 설치되어 있지 않습니다."
fi

##############################################
# MySQL 업그레이드
##############################################
echo "========================================"
echo "MySQL 업그레이드 중..."
echo "========================================"

if command -v mysql &> /dev/null; then
    echo "현재 MySQL 버전: $(mysql --version)"
    
    # MySQL 백업 권장 메시지
    echo "⚠️  경고: MySQL 업그레이드 전 백업을 권장합니다!"
    echo "백업 명령어: sudo mysqldump --all-databases > backup.sql"
    
    read -p "계속하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $OS in
            ubuntu|debian)
                sudo apt install -y --only-upgrade mysql-server mysql-client
                ;;
            centos|rhel|fedora|amzn)
                sudo yum update -y mysql-community-server
                ;;
        esac
        
        # MySQL 업그레이드 실행
        sudo mysql_upgrade -u root -p || echo "mysql_upgrade가 필요하지 않거나 실패했습니다."
        sudo systemctl restart mysqld || sudo systemctl restart mysql
        
        echo "업그레이드된 MySQL 버전: $(mysql --version)"
    else
        echo "MySQL 업그레이드를 건너뜁니다."
    fi
else
    echo "MySQL이 설치되어 있지 않습니다."
fi

##############################################
# PostgreSQL 업그레이드
##############################################
echo "========================================"
echo "PostgreSQL 확인 중..."
echo "========================================"

if command -v psql &> /dev/null || [ -f /usr/pgsql-16/bin/psql ]; then
    echo "PostgreSQL이 설치되어 있습니다."
    
    if [ -f /usr/pgsql-16/bin/psql ]; then
        echo "현재 PostgreSQL 버전: $(/usr/pgsql-16/bin/psql --version)"
    else
        echo "현재 PostgreSQL 버전: $(psql --version)"
    fi
    
    echo "⚠️  PostgreSQL 메이저 버전 업그레이드는 수동 작업이 필요합니다."
    echo "마이너 버전 업데이트만 진행합니다."
    
    case $OS in
        ubuntu|debian)
            sudo apt install -y --only-upgrade postgresql postgresql-contrib
            ;;
        centos|rhel|fedora|amzn)
            sudo yum update -y postgresql16-server postgresql16
            ;;
    esac
else
    echo "PostgreSQL이 설치되어 있지 않습니다."
fi

##############################################
# MongoDB 업그레이드
##############################################
echo "========================================"
echo "MongoDB 업그레이드 중..."
echo "========================================"

if command -v mongod &> /dev/null; then
    echo "현재 MongoDB 버전:"
    mongod --version | head -n 1
    
    echo "⚠️  경고: MongoDB 업그레이드 전 백업을 권장합니다!"
    echo "백업 명령어: mongodump --out=/backup/mongodb"
    
    read -p "계속하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $OS in
            ubuntu|debian)
                sudo apt install -y --only-upgrade mongodb-org
                ;;
            centos|rhel|fedora|amzn)
                sudo yum update -y mongodb-org
                ;;
        esac
        
        sudo systemctl restart mongod
        
        echo "업그레이드된 MongoDB 버전:"
        mongod --version | head -n 1
    else
        echo "MongoDB 업그레이드를 건너뜁니다."
    fi
else
    echo "MongoDB가 설치되어 있지 않습니다."
fi

##############################################
# 업그레이드 완료 및 요약
##############################################
echo ""
echo "========================================"
echo "업그레이드 완료!"
echo "========================================"
echo ""
echo "현재 설치된 버전:"
echo "----------------------------------------"

if command -v node &> /dev/null; then
    echo "Node.js: $(node --version)"
    echo "npm: $(npm --version)"
fi

if command -v python3.11 &> /dev/null; then
    echo "Python: $(python3.11 --version)"
    echo "pip: $(python3.11 -m pip --version)"
elif command -v python3 &> /dev/null; then
    echo "Python: $(python3 --version)"
fi

if command -v java &> /dev/null; then
    echo "Java: $(java -version 2>&1 | head -n 1)"
fi

if command -v mysql &> /dev/null; then
    echo "MySQL: $(mysql --version)"
fi

if command -v psql &> /dev/null; then
    echo "PostgreSQL: $(psql --version)"
elif [ -f /usr/pgsql-16/bin/psql ]; then
    echo "PostgreSQL: $(/usr/pgsql-16/bin/psql --version)"
fi

if command -v mongod &> /dev/null; then
    echo "MongoDB: $(mongod --version | head -n 1)"
fi

echo "----------------------------------------"
echo ""
echo "⚠️  중요 참고사항:"
echo "1. 데이터베이스 업그레이드 후에는 애플리케이션 테스트를 권장합니다."
echo "2. 메이저 버전 업그레이드는 별도의 마이그레이션 계획이 필요합니다."
echo "3. 백업이 정상적으로 되어 있는지 확인하세요."
