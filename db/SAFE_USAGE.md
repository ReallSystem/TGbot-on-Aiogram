# 🛡️ Рекомендована схема безпечного користування БД в обробниках

## ❌ Небезпечно (раніше)

```python
async def handle_message(message: types.Message):
    db = SessionLocal()
    user = get_or_create_user(db, message.from_user.id)
    add_message(db, user.id, message.text)
    db.close()  # ❌ Якщо помилка, БД не закриється
```

## ✅ Безпечно (правильно)

### Варіант 1: Context Manager (РЕКОМЕНДУЄТЬСЯ)

```python
from contextlib import contextmanager
from db import SessionLocal

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_message(message: types.Message):
    with get_db_session() as db:
        user = get_or_create_user(db, message.from_user.id)
        if user:  # ✅ Перевіряємо результат
            add_message(db, user.id, message.text)
            await message.answer("✅ Повідомлення збережено")
        else:
            await message.answer("❌ Помилка при збереженні")
```

### Варіант 2: Try-Except блок

```python
async def handle_start(message: types.Message):
    db = SessionLocal()
    try:
        user = get_or_create_user(
            db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        if user:
            log_action(db, user.id, "command", "/start")
            add_message(db, user.id, message.text, "command")
            await message.answer(f"Привіт, {message.from_user.first_name}! 👋")
        else:
            await message.answer("Помилка при реєстрації")

    except Exception as e:
        logger.error(f"Error in handle_start: {e}")
        await message.answer("⚠️ Сервісна помилка. Спробуйте пізніше.")

    finally:
        db.close()
```

### Варіант 3: Dependency Injection (для великих проектів)

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_db_session():
    return SessionLocal()

async def handle_message(message: types.Message, db = Depends(get_db_session)):
    user = get_or_create_user(db, message.from_user.id)
    # ... ваш код
```

## 🔍 Перевірка результатів функцій

```python
async def handle_stats(message: types.Message):
    db = SessionLocal()
    try:
        # ✅ Завжди перевіряйте результати функцій
        stats = get_statistics(db)
        if stats and stats.get('total_users', 0) > 0:
            response = f"📊 Користувачів: {stats['total_users']}"
            await message.answer(response)
        else:
            await message.answer("📊 Статистика недоступна")

    finally:
        db.close()
```

## 📝 Логування

```python
import logging

logger = logging.getLogger(__name__)

async def handle_button_click(callback_query: types.CallbackQuery):
    db = SessionLocal()
    try:
        user = get_or_create_user(db, callback_query.from_user.id)

        if user:
            action = log_action(db, user.id, "button_click", "my_button")

            # ✅ Логуйте без чутливих даних
            logger.info(f"User {user.telegram_id} clicked button")

            await callback_query.answer("✅ Дія записана")
        else:
            logger.warning(f"Failed to get user {callback_query.from_user.id}")
            await callback_query.answer("❌ Помилка")

    except Exception as e:
        # ❌ Не логуйте повні stack traces користувачу!
        logger.error(f"Button click error: {e}", exc_info=True)
        await callback_query.answer("⚠️ Помилка. Спробуйте пізніше.")

    finally:
        db.close()
```

## 🚀 Готовий шаблон для dispatcher.py

```python
import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from db import SessionLocal
from db.queries import get_or_create_user, add_message, log_action

logger = logging.getLogger(__name__)

def create_dispatcher():
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        db = SessionLocal()
        try:
            user = get_or_create_user(
                db,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )

            if user:
                log_action(db, user.id, "command", "/start")
                add_message(db, user.id, message.text, "command")
                await message.answer(f"Привіт, {message.from_user.first_name}!")
            else:
                logger.error(f"Failed to create user {message.from_user.id}")
                await message.answer("Помилка при реєстрації")

        except Exception as e:
            logger.error(f"Error in cmd_start: {e}")
            await message.answer("⚠️ Сервісна помилка")

        finally:
            db.close()

    return dp
```

## ✅ Контрольний список

- [ ] Всі функції повертають результат (не None)
- [ ] Всі DB операції в try-except блоках
- [ ] БД сесія завжди закривається (finally блок)
- [ ] Помилки логуються, але не відправляються користувачу
- [ ] Параметри перевіряються перед передачею в DB
- [ ] Очні помилок не містять чутливу інформацію
