# 🛡️ Приклади використання Rate Limiting

## Базовий приклад - Перевірка ліміту перед збереженням

```python
from aiogram import types
from db import SessionLocal
from db.queries import get_or_create_user, add_message
from db.rate_limit import check_rate_limit

async def handle_text_message(message: types.Message):
    """Обробник текстового повідомлення з rate limiting"""
    db = SessionLocal()
    try:
        user = get_or_create_user(db, message.from_user.id)

        if not user:
            await message.answer("❌ Помилка при реєстрації")
            return

        # ✅ Перевірити ліміт на повідомлення
        allowed, error_msg = check_rate_limit(db, user.id, "messages")

        if not allowed:
            await message.answer(error_msg)  # Повідомити користувачу
            return

        # Якщо все нормально - записати повідомлення
        add_message(db, user.id, message.text)
        await message.answer("✅ Повідомлення збережено")

    finally:
        db.close()
```

## Приклад 2 - Rate Limit для кнопок

```python
from db.rate_limit import check_rate_limit

async def handle_button_click(callback_query: types.CallbackQuery, button_name: str):
    """Обробник клику на кнопку"""
    db = SessionLocal()
    try:
        user = get_or_create_user(db, callback_query.from_user.id)

        if not user:
            await callback_query.answer("❌ Помилка", show_alert=True)
            return

        # ✅ Перевірити ліміт на кліки кнопок
        allowed, error_msg = check_rate_limit(db, user.id, "button_click")

        if not allowed:
            await callback_query.answer(error_msg, show_alert=True)
            return

        # Обробити клік
        log_action(db, user.id, "button_click", button_name)
        await callback_query.answer(f"✅ {button_name} активовано")

    finally:
        db.close()
```

## Приклад 3 - Показати статус лімітів користувачу

```python
from db.rate_limit import get_rate_limit_status

async def handle_status_command(message: types.Message):
    """Команда /status - показати статус лімітів"""
    db = SessionLocal()
    try:
        user = get_or_create_user(db, message.from_user.id)

        if not user:
            return

        # Отримати статус всіх лімітів
        status = get_rate_limit_status(db, user.id)

        response = "📊 **Статус ваших лімітів:**\n\n"

        for action_type, limits in status.items():
            emoji = "✅" if not limits["limited"] else "⏱️"
            response += (
                f"{emoji} **{action_type}**: {limits['current']}/{limits['max']}\n"
                f"   Залишилось: {limits['remaining']}\n\n"
            )

        await message.answer(response)

    finally:
        db.close()
```

## Приклад 4 - Адмін команда для перегляду активних користувачів

```python
from db.rate_limit import get_most_active_users
from handlers.admin import AdminFilter

@router.message(Command("activity"), AdminFilter())
async def handle_activity_command(message: types.Message):
    """Адмін команда - активність користувачів (тільки для адмінів)"""
    db = SessionLocal()
    try:
        # Отримати топ 10 найактивніших користувачів за остану годину
        active_users = get_most_active_users(db, limit=10, window_minutes=60)

        if not active_users:
            await message.answer("📊 Немає активності")
            return

        response = "👥 **Найактивніші користувачі за останню годину:**\n\n"

        for idx, (user_id, action_count) in enumerate(active_users, 1):
            response += f"{idx}. User ID: {user_id} - {action_count} дій\n"

        await message.answer(response)

    finally:
        db.close()
```

## Налаштування лімітів

Якщо хочете змінити ліміти, змініть у `db/rate_limit.py`:

```python
RATE_LIMITS = {
    "messages": {
        "max_count": 50,      # змініть на потрібну кількість
        "window_seconds": 60  # zmініть на потрібну кількість секунд
    },
    "button_click": {
        "max_count": 30,
        "window_seconds": 60
    },
    "command": {
        "max_count": 20,
        "window_seconds": 60
    }
}
```

## Таблиця рекомендованих лімітів

| Дія | Кількість | За час | Обґрунтування |
| --- | --- | --- | --- |
| Повідомлення | 50 | 1 хв | Розумне користування |
| Клік кнопки | 30 | 1 хв | Запобігання спаму |
| Команди | 20 | 1 хв | Запобігання DDoS |
| Довгі рядки | 10 | 1 хв | Для обмеження батарей |

## Тестування Rate Limit

```python
# Швидкий тест
async def test_rate_limit():
    db = SessionLocal()
    user_id = 123

    # Перевірити 5 разів підряд
    for i in range(5):
        allowed, msg = check_rate_limit(db, user_id, "messages")
        print(f"Спроба {i+1}: {'✅ Дозволено' if allowed else '❌ Блоковано'}")

    db.close()
```
