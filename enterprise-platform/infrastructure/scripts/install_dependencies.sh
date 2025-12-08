#!/bin/bash
# Run as root
echo ">>> 📦 Updating System and Installing Dependencies..."
apt-get update && apt-get upgrade -y

# 1. Install Java (OpenJDK 17)
apt-get install -y openjdk-17-jdk

# 2. Install Python & Pip
apt-get install -y python3 python3-pip python3-venv

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# 4. Install Docker Compose
apt-get install -y docker-compose-plugin

echo ">>> ✅ Installation Complete!"
java -version
python3 --version
docker --version
