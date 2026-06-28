#!/bin/bash
# ==========================================
# Script de durcissement OS - Pare-feu UFW
# ==========================================

echo "🛡️ Configuration du pare-feu UFW en cours..."

# 1. Règles par défaut (Principe du moindre privilège)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. Ouvertures strictes
sudo ufw allow 22/tcp # Autorise SSH pour l'administration
sudo ufw allow 80/tcp # Autorise le trafic HTTP vers notre Reverse Proxy Nginx

# 3. Activation
sudo ufw --force enable
echo "Pare-feu activé et durci avec succès !"