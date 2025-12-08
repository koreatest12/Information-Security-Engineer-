#!/bin/bash
# Run as root
echo ">>> 🛡️ Configuring System Firewall (UFW)..."

# Reset UFW
ufw --force reset

# Default Policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (Port 22) - Essential!
ufw allow 22/tcp

# Allow App Ports
ufw allow 8080/tcp comment 'Spring Boot'
ufw allow 8000/tcp comment 'FastAPI'

# Allow Database (Optional, generic)
# ufw allow 5432/tcp 

# Enable Firewall
echo "y" | ufw enable

echo ">>> 🔥 Firewall Status:"
ufw status verbose
