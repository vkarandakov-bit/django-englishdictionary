# EnglishCard — Django-версия

Интерактивное веб-приложение для эффективного запоминания английских слов методом викторины,
ведения личного словаря и отслеживания прогресса обучения.
Использует **Django** как веб-фреймворк.

## Возможности

- вход по логину без пароля (как в оригинале);
- викторина «выбери правильный перевод» из 4 вариантов;
- добавление личных слов;
- персональное удаление слов (в том числе базовых);
- статистика попыток и точности;
- просмотр схемы базы данных.

## Быстрый запуск

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_common_words
python manage.py runserver
```

Откройте http://127.0.0.1:8000/

## PostgreSQL

Скопируйте `example.env` в `.env` и укажите параметры подключения:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=english_card
```

Если `DB_HOST` не задан, проект использует SQLite.

## Структура

- `dictionary/models.py` — модели БД 
- `dictionary/services.py` — бизнес-логика 
- `dictionary/views.py` — страницы приложения 
- `dictionary/templates/` — HTML-шаблоны интерфейса

