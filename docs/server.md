# Сервер: схема и изоляция проектов

Один VPS. Сейчас на нём только Levefit, но схема рассчитана на то, что позже появятся другие
проекты: они не будут делить порты, сети, базы и секреты.

## Схема

```text
Интернет :80/:443
      │
 ┌────▼────────────────────┐   сеть edge (общая, только для входящего трафика)
 │ proxy (Caddy, HTTPS)    │───────────────┬───────────────────────┐
 └─────────────────────────┘               │                       │
                                  levefit-web (alias)     <другой проект> (alias)
 проект levefit (своя сеть)                │                  позже, по необходимости
   db ─ api ─ bot ─ web ───────────────────┘
```

- Единственный, кто слушает порты 80/443 на хосте, — общий прокси (`infra/proxy`). Он же получает сертификаты Let's Encrypt.
- Каждый проект — отдельный `docker compose` с собственным именем (`name:`), своей внутренней сетью и своими томами. База Levefit (Postgres) и API недоступны извне и из других проектов.
- В сеть `edge` проект выставляет только один «входной» сервис с уникальным alias (`levefit-web`, у другого проекта — своё). Имена не пересекаются.
- Порты на хост проекты не публикуют (иначе Docker обходит файрвол ufw).
- У каждого проекта лимиты памяти (`mem_limit`), чтобы один не съел всё.
- Секреты: `/opt/levefit/.env.prod` принадлежит root (права 600), каталог закрыт (750), посторонним процессам он недоступен.

## Настройка сервера (`infra/server/bootstrap.sh`)

Скрипт идемпотентный, запускается от root по ключу: `ssh root@сервер 'bash -s' < infra/server/bootstrap.sh`.

- Обновления безопасности автоматически (`unattended-upgrades`).
- SSH только по ключам, без входа root по паролю; `fail2ban` против подбора.
- `ufw`: входящие закрыты, открыты SSH, 80 и 443.
- Отключены ненужные службы (snapd, ModemManager, cups, avahi, bluetooth, rpcbind, apport, multipathd, packagekit, udisks2 и т. п.), если они есть.
- Docker из официального репозитория; логи контейнеров ограничены (10 МБ × 3).
- Созданы сеть `edge` и каталоги `/opt/proxy`, `/opt/levefit` (root:root 750).

## Как позже добавить ещё один проект

1. Каталог `/opt/<проект>`, свой `docker-compose.yml` с уникальным `name:`.
2. Входной сервис подключить к сети `edge` с уникальным alias; портов на хост не публиковать; задать `mem_limit`.
3. В `/opt/proxy/sites/<проект>.caddy` описать свой (под)домен и `reverse_proxy <alias>:<порт>` (образец: `levefit.caddy.template`).
4. `docker compose -f /opt/proxy/docker-compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile`.
5. Субдомены sslip.io (`app.203-0-113-5.sslip.io`) резолвятся в тот же IP, сертификат выпускается автоматически.

Важно: доступ к Docker (группа `docker`, сокет `/var/run/docker.sock`) равен root. Агентным приложениям его не давать:
иначе они смогут прочитать секреты Levefit.

## Текущее развёртывание

- Сервер: Ubuntu 24.04, 1 vCPU, ~1 ГБ RAM (+1 ГБ свопа), 10 ГБ диска; IP `217.177.72.87`.
- Адрес Mini App: `https://217-177-72-87.sslip.io` (сертификат Let's Encrypt, продлевается Caddy автоматически).
- Запущено: `proxy-caddy-1` (80/443), `levefit-web-1`, `levefit-api-1`, `levefit-bot-1`, `levefit-db-1` (Postgres). Контейнеры вместе занимают ~215 МБ.
- Из интернета доступны только порты 22 (SSH только по ключу), 80, 443 и 8080 (панель хостера BeAdmin; при желании закрывается командой `ufw delete allow 8080/tcp`).
- Секреты лежат в `/opt/levefit/.env.prod` (root, права 600) и сгенерированы на сервере; токен бота скопирован из локального `.env`.
- Снаружи закрыты `/api/internal/*` (служебные запросы бота идут внутри сети compose).

Обновление: `scripts/deploy_vps.sh` (заливает текущий коммит и пересобирает).
Включить ИИ-рекомендации: вписать `ANTHROPIC_API_KEY=...` в `/opt/levefit/.env.prod` и выполнить
`cd /opt/levefit && docker compose -f docker-compose.prod.yml --env-file .env.prod up -d api`.
Копия базы: `docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db pg_dump -U levefit levefit > backup.sql`.
