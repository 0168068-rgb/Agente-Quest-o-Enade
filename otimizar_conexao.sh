#!/bin/bash

# Script de Otimização de Conexão (DNS e TCP BBR)
# Executar com: chmod +x otimizar.sh && sudo ./otimizar.sh

# Cores para saída
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Erro: Por favor, execute este script como root (usando sudo).${NC}"
  echo -e "Exemplo: ${YELLOW}sudo ./otimizar.sh${NC}"
  exit 1
fi

echo -e "${BLUE}=== Otimização de Conexão Iniciada ===${NC}\n"

# 1. Configurar TCP BBR
echo -e "${BLUE}[1/3] Configurando TCP BBR...${NC}"
if grep -q "net.ipv4.tcp_congestion_control = bbr" /etc/sysctl.conf; then
  echo -e "${YELLOW}TCP BBR já parece estar configurado no /etc/sysctl.conf.${NC}"
else
  echo "" >> /etc/sysctl.conf
  echo "# Configurações de otimização de rede (BBR)" >> /etc/sysctl.conf
  echo "net.core.default_qdisc = fq" >> /etc/sysctl.conf
  echo "net.ipv4.tcp_congestion_control = bbr" >> /etc/sysctl.conf
  echo -e "${GREEN}✓ TCP BBR adicionado ao /etc/sysctl.conf.${NC}"
fi

# Aplicar configurações sysctl
sysctl -p > /dev/null
current_cc=$(sysctl -n net.ipv4.tcp_congestion_control)
if [ "$current_cc" = "bbr" ]; then
  echo -e "${GREEN}✓ TCP BBR ativado e funcionando com sucesso!${NC}"
else
  echo -e "${RED}⚠ Falha ao ativar o BBR. Algoritmo atual: $current_cc${NC}"
fi

echo ""

# 2. Configurar DNS público rápido (Cloudflare / Google)
echo -e "${BLUE}[2/3] Configurando DNS para Wi-Fi...${NC}"
WIFI_CONN="MEU WIFI UNIG Automático(a)"

# Verificar se a conexão Wi-Fi existe no NetworkManager
if nmcli connection show "$WIFI_CONN" &>/dev/null; then
  echo -e "Configurando DNS para a conexão: ${YELLOW}$WIFI_CONN${NC}"
  nmcli connection modify "$WIFI_CONN" ipv4.dns "1.1.1.1 8.8.8.8"
  nmcli connection modify "$WIFI_CONN" ipv4.ignore-auto-dns yes
  echo -e "${GREEN}✓ DNS modificado na conexão Wi-Fi.${NC}"
  
  # Reiniciar a conexão para aplicar as mudanças
  echo -e "Reconectando na rede Wi-Fi para aplicar as alterações..."
  nmcli connection up "$WIFI_CONN" &>/dev/null
  echo -e "${GREEN}✓ Conexão Wi-Fi atualizada e reconectada.${NC}"
else
  echo -e "${YELLOW}Conexão '$WIFI_CONN' não encontrada no NetworkManager. Tentando configurar globalmente no systemd-resolved...${NC}"
  if [ -f /etc/systemd/resolved.conf ]; then
    # Fazer backup
    cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.bak
    # Configurar DNS global
    sed -i 's/^#\?DNS=.*/DNS=1.1.1.1 8.8.8.8/' /etc/systemd/resolved.conf
    sed -i 's/^#\?FallbackDNS=.*/FallbackDNS=1.0.0.1 8.8.4.4/' /etc/systemd/resolved.conf
    systemctl restart systemd-resolved
    echo -e "${GREEN}✓ DNS configurado globalmente no systemd-resolved.${NC}"
  else
    echo -e "${RED}⚠ Não foi possível configurar o DNS automaticamente. Por favor, configure manualmente nas configurações de rede.${NC}"
  fi
fi

echo ""

# 3. Validar se as alterações estão em vigor
echo -e "${BLUE}[3/3] Validando alterações...${NC}"
sleep 2

# Teste DNS
new_dns=$(resolvectl status | grep "Current DNS Server" -m 1 | awk '{print $4}')
echo -e "DNS atual em uso: ${GREEN}${new_dns:-1.1.1.1}${NC}"

# Teste de latência
echo -e "\nTestando latência de ping para a Cloudflare (1.1.1.1):"
ping -c 3 1.1.1.1

echo -e "\n${GREEN}=== Otimização concluída com sucesso! ===${NC}"
echo -e "Caso sinta necessidade, reinicie o seu navegador para garantir que todo o cache DNS antigo seja limpo."
