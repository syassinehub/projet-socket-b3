#!/bin/bash
set -euo pipefail

echo "Configuration du pare-feu UFW..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH administration'
sudo ufw allow 80/tcp comment 'SOCket reverse proxy HTTP'
sudo ufw --force enable
sudo ufw status verbose
