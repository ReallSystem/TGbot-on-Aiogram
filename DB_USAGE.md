# Як використовувати БД

## Приклад 1: Зареєструвати користувача

```python
from db import SessionLocal
from db.queries import get_or_create_user

db = SessionLocal()
user = get_or_create_user(
    db,
    telegram_id=123456,
    username="john",
    first_name="John"
)
db.close()
```

## Приклад 2: Зберегти повідомлення

```python
from db.queries import add_message

add_message(
    db,
    user_id=user.id,
    text="Привіт!",
    message_type="text"
)
```

## Приклад 3: Залогувати дію

```python
from db.queries import log_action

log_action(
    db,
    user_id=user.id,
    action_type="button_click",
    action_name="📚 Каталог"
)
```

## Приклад 4: Отримати статистику

```python
from db.queries import get_statistics, get_top_actions

stats = get_statistics(db)
print(f"Користувачів: {stats['total_users']}")
print(f"Повідомлень: {stats['total_messages']}")
print(f"Дій: {stats['total_actions']}")

top_actions = get_top_actions(db, limit=5)
for action in top_actions:
    print(f"{action.action_name}: {action.count}")
```

## Усі функції

| Функція | Призначення |
| --- | --- |
| get_or_create_user | Отримати або створити користувача |
| get_user | Отримати користувача |
| add_message | Зберегти повідомлення |
| log_action | Залогувати дію |
| get_statistics | Загальна статистика |
| get_top_actions | Топ популярних дій |

## Важливо

ОК — Завжди закривайте сесію: `db.close()`
ОК — Функції повертають None на помилку
ОК — Помилки логуються автоматично
