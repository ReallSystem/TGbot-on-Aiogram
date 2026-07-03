# PostgreSQL на Railway

## Що зроблено

ОК — Код переписаний для PostgreSQL
ОК — Драйвер psycopg2-binary добавлений  
ОК — Обробка помилок налаштована

## Крок 1: Закомітьте зміни

```bash
git add .
git commit -m "feat: switch to PostgreSQL on Railway"
git push origin main
```

## Крок 2: На Railway Dashboard

1. Перейти на <https://railway.app/dashboard>
2. Вибрати проект Verbel-bot
3. Натиснути New → Database → PostgreSQL
4. Railway автоматично створить DATABASE_URL

## Крок 3: Перевірка логів

Логи повинні показати:

```text
✅ Database tables initialized successfully
```

## Що далі

- Дані зберігаються в PostgreSQL
- Таблиці: users, chat_messages, user_actions
- Переглядати через Data Browser на Railway
- Дані зберігаються постійно навіть після перезапуску
