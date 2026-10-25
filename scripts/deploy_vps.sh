#!/usr/bin/env bash
# Обновляет Levefit на сервере: заливает текущий коммит, пересобирает и перезапускает контейнеры.
# Секреты (.env.prod) остаются на сервере и не перезаписываются.
# Использование: scripts/deploy_vps.sh [user@host] [путь_к_ключу]
set -euo pipefail

TARGET="${1:-root@217.177.72.87}"
KEY="${2:-$HOME/.ssh/levefit_vps}"
SSH=(ssh -i "$KEY" -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=20 "$TARGET")

archive="$(mktemp)"
git archive --format=tar.gz -o "$archive" HEAD
"${SSH[@]}" 'cat > /tmp/levefit.tar.gz' < "$archive"
rm -f "$archive"

"${SSH[@]}" 'bash -s' <<'EOF'
set -euo pipefail
cd /opt/levefit
tar -xzf /tmp/levefit.tar.gz && rm -f /tmp/levefit.tar.gz
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker image prune -f > /dev/null
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
EOF
