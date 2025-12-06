# Тестирование Backend

## Требования

```bash
pip install pytest pytest-asyncio httpx
```

## Запуск тестов для Auth Service

```bash
cd auth-service
pytest tests/test_auth.py -v
```

## Запуск тестов для Tasks Service

```bash
cd tasks-service
pytest tests/test_tasks.py -v
```

## Запуск всех тестов

```bash
cd auth-service && pytest && cd ..
cd tasks-service && pytest && cd ..
```

## Структура тестов

### Auth Service Tests (`tests/test_auth.py`)
- `test_register_user` - Регистрация нового пользователя
- `test_register_duplicate_email` - Попытка зарегистрировать пользователя с существующим email
- `test_login_success` - Успешная аутентификация
- `test_login_invalid_password` - Ошибка: неверный пароль
- `test_login_nonexistent_user` - Ошибка: пользователь не существует
- `test_get_users` - Получение списка пользователей
- `test_invalid_registration_data` - Валидация данных при регистрации
- `test_verify_token` - Проверка JWT токена
- `test_verify_invalid_token` - Ошибка: невалидный токен

### Tasks Service Tests (`tests/test_tasks.py`)
- `test_create_task` - Создание новой задачи
- `test_get_tasks` - Получение списка задач
- `test_get_task_by_id` - Получение задачи по ID
- `test_update_task` - Обновление задачи
- `test_delete_task` - Удаление задачи
- `test_task_validation` - Валидация данных задачи
- `test_add_worker_to_task` - Назначение работника на задачу
- `test_complete_task_by_worker` - Отметка выполнения работником
- `test_filter_tasks_by_status` - Фильтрация задач по статусу

## Примеры запуска

```bash
# Запустить конкретный тест
pytest tests/test_auth.py::test_login_success -v

# Запустить с покрытием кода
pytest tests/ --cov=app --cov-report=html

# Запустить с подробным выводом
pytest tests/ -vv -s

# Запустить только тесты с определённым именем
pytest tests/ -k "test_login"
```

## Интеграционные тесты

Все тесты используют in-memory SQLite базу для изоляции и скорости. После запуска каждого теста база очищается.
