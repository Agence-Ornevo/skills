#!/usr/bin/env bash
# Ornevo Production Server — Quick Health Check Script
# Run from local machine with SSH access to ornevo server
# Usage: ./ornevo-health-check.sh

set -euo pipefail

ORNEVO_HOST="ornevo"
DOMAINS=(
  "n8n.ornevo.pro"
  "chat.ornevo.pro"
  "project.ornevo.pro"
  "docmost.ornevo.pro"
  "pm.ornevo.pro"
  "status.ornevo.pro"
)

echo "=========================================="
echo "Ornevo Production Server Health Check"
echo "Date: $(date -u)"
echo "=========================================="
echo ""

echo "--- Container Fleet ---"
ssh "$ORNEVO_HOST" "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'"

echo ""
echo "--- Unhealthy Containers ---"
ssh "$ORNEVO_HOST" "docker ps --filter health=unhealthy --format '{{.Names}}' || echo 'None'"

echo ""
echo "--- System Resources ---"
ssh "$ORNEVO_HOST" "df -h / && free -h && uptime"

echo ""
echo "--- External Domain Health ---"
for domain in "${DOMAINS[@]}"; do
  printf "%-30s " "$domain"
  if curl -s -o /dev/null -w "%{http_code} %{time_total}s" --max-time 10 "https://$domain" 2>/dev/null; then
    echo ""
  else
    echo "FAILED"
  fi
done

echo ""
echo "--- SSL Certificate Expiry ---"
for domain in "${DOMAINS[@]}"; do
  printf "%-30s " "$domain"
  if expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2); then
    echo "$expiry"
  else
    echo "FAILED"
  fi
done

echo ""
echo "--- n8n Health Endpoint ---"
printf "n8n.ornevo.pro/healthz: "
curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 "https://n8n.ornevo.pro/healthz"

echo ""
echo "--- Docker Disk Usage ---"
ssh "$ORNEVO_HOST" "docker system df"

echo ""
echo "--- OS Package Updates ---"
ssh "$ORNEVO_HOST" "apt list --upgradable 2>/dev/null | wc -l | xargs -I{} echo '{} packages upgradable'"

echo ""
echo "=========================================="
echo "Health check complete"
echo "=========================================="