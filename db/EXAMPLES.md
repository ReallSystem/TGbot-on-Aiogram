# Приклади використання БД

Приклад: як використовувати БД в обробниках

Переконайтеся, що вже встановлені залежності:
    pip install -r requirements.txt

## Приклад 1: Реєстрація користувача при /start

```python
from aiogram import types
from db import SessionLocal
from db.queries import get_or_create_user, add_message, log_action

async def handle_start(message: types.Message):
    """Обробник команди /start"""
    db = SessionLocal()

    # Отримати або створити користувача
    user = get_or_create_user(
        db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    # Записати дію
    log_action(db, user.id, "command", "/start")

    # Записати повідомлення
    add_message(db, user.id, message.text, "command")

    db.close()

    await message.answer(f"Привіт, {message.from_user.first_name}! 👋")
```

## Приклад 2: Обробник звичайного повідомлення

```python
async def handle_text_message(message: types.Message):
    """Обробник текстового повідомлення"""
    db = SessionLocal()

    user = get_or_create_user(db, message.from_user.id)

    # Записати повідомлення
    add_message(db, user.id, message.text)

    db.close()

    await message.answer("Повідомлення отримано!")
```

## Приклад 3: Отримати топ дій

```python
from db.queries import get_top_actions, get_statistics

async def handle_stats_command(message: types.Message):
    """Обробник команди /stats"""
    db = SessionLocal()

    # Отримати статистику
    stats = get_statistics(db)

    # Отримати топ популярних дій
    top_actions = get_top_actions(db, limit=5)

    response = f"""
📊 Статистика:
👥 Користувачів: {stats['total_users']}
💬 Повідомлень: {stats['total_messages']}
🎯 Дій: {stats['total_actions']}

📈 Топ 5 дій:
"""

    for i, action in enumerate(top_actions, 1):
        response += f"{i}. {action.action_name} - {action.count} разів\n"

    db.close()

    await message.answer(response)
```

## Приклад 4: Обробник кнопки

```python
async def handle_button_click(callback_query: types.CallbackQuery, button_name: str):
    """Обробник клику на кнопку"""
    db = SessionLocal()

    user = get_or_create_user(db, callback_query.from_user.id)

    # Записати дію
    log_action(db, user.id, "button_click", button_name)

    db.close()

    await callback_query.answer(f"Ви натиснули: {button_name}")
```
