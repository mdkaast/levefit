#!/usr/bin/env bash
# Первичная подготовка чистого Ubuntu 22.04/24.04 (запускать от root, по SSH-ключу).
# Идемпотентный: повторный запуск ничего не ломает. Делает:
#   1) обновления безопасности, SSH только по ключам, ufw (только SSH/80/443), fail2ban;
#   2) отключает ненужные для сервера службы;
#   3) ставит Docker из официального репозитория, ограничивает размер логов контейнеров;
#   4) создаёт общую сеть edge и каталоги /opt/proxy, /opt/levefit.
# Использование: ssh root@сервер 'bash -s' < infra/server/bootstrap.sh
set -euo pipefail

log() { printf '\n==> %s\n' "$*"; }

if [ "$(id -u)" -ne 0 ]; then echo "Запустите от root"; exit 1; fi
. /etc/os-release
if [ "${ID:-}" != "ubuntu" ]; then echo "Скрипт рассчитан на Ubuntu, найден: ${ID:-?}"; exit 1; fi
export DEBIAN_FRONTEND=noninteractive

log "Состояние до настройки: слушающие порты"
ss -tulpnH | awk '{print $1, $5, $7}' | sort -u || true

# ---------- 1. пакеты, обновления, защита ----------
log "Обновление списка пакетов и установка базовых"
apt-get update -y
apt-get install -y ca-certificates curl gnupg ufw fail2ban unattended-upgrades

log "Автоматические обновления безопасности"
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

log "SSH: только ключи (проверка конфигурации перед применением)"
# Страховка: не закрываем вход по паролю, если у root нет ни одного ключа.
if [ -s /root/.ssh/authorized_keys ] || ls /home/*/.ssh/authorized_keys >/dev/null 2>&1; then
  mkdir -p /etc/ssh/sshd_config.d
  cat > /etc/ssh/sshd_config.d/99-hardening.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
MaxAuthTries 3
X11Forwarding no
EOF
  sshd -t
  systemctl reload ssh || systemctl reload sshd
else
  echo "ПРОПУЩЕНО: нет ни одного authorized_keys, вход по паролю оставлен"
fi

log "Файрвол ufw: входящие закрыты, открыты только SSH, 80, 443"
SSH_PORT="$(sshd -T | awk '/^port /{print $2; exit}')"
ufw default deny incoming
ufw default allow outgoing
ufw allow "${SSH_PORT:-22}/tcp" comment 'ssh'
ufw allow 80/tcp comment 'http (acme, redirect)'
ufw allow 443/tcp comment 'https'
# Дополнительные порты (например, панель хостера): EXTRA_TCP_PORTS="8080" bash -s
for extra in ${EXTRA_TCP_PORTS:-}; do ufw allow "${extra}/tcp" comment 'extra'; done
ufw --force enable

log "fail2ban для SSH"
cat > /etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
EOF
systemctl enable --now fail2ban
systemctl restart fail2ban

# ---------- 2. ненужные службы ----------
log "Отключение ненужных служб (если установлены)"
for svc in snapd.socket snapd.service ModemManager.service cups.service cups-browsed.service \
           avahi-daemon.socket avahi-daemon.service bluetooth.service rpcbind.socket rpcbind.service \
           apport.service motd-news.timer lxd-agent.service multipathd.socket multipathd.service \
           packagekit.service udisks2.service; do
  if systemctl list-unit-files "$svc" --no-legend 2>/dev/null | grep -q .; then
    systemctl disable --now "$svc" 2>/dev/null && echo "отключено: $svc" || true
  fi
done

# ---------- 3. Docker ----------
if ! command -v docker >/dev/null 2>&1; then
  log "Установка Docker из официального репозитория"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME:-$VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

log "Настройки Docker: ограничение логов, live-restore"
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true
}
EOF
systemctl enable --now docker
systemctl restart docker

# ---------- 4. сети, каталоги, права ----------
log "Общая сеть для входящего трафика (edge)"
docker network inspect edge >/dev/null 2>&1 || docker network create edge

log "Каталоги проектов"
# Каталоги закрыты для всех, кроме root: секреты .env.prod недоступны посторонним процессам.
install -d -m 750 -o root -g root /opt/proxy /opt/levefit

log "Своп (если памяти мало и свопа нет)"
MEM_MB="$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)"
if [ "$MEM_MB" -le 2048 ] && ! swapon --show --noheadings | grep -q .; then
  SWAP_SIZE="2G"; [ "$MEM_MB" -le 1100 ] && SWAP_SIZE="1G"   # на малых дисках не отдаём лишнее
  fallocate -l "$SWAP_SIZE" /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

log "Готово. Состояние после настройки: слушающие порты"
ss -tulpnH | awk '{print $1, $5, $7}' | sort -u || true
ufw status verbose | head -12
docker --version
docker compose version
