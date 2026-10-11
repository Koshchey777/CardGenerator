# Fast OG Card Generator API

API для генерации социальных карточек (Open Graph images).

## Возможности

- 4 шаблона карточек (простой, градиент, magazine, quote)
- Авто-контраст текста
- Поддержка разных размеров (Twitter, Facebook, Instagram, LinkedIn)
- Кэширование для ускорения повторных запросов

## Документация

После деплоя доступна по адресу: `/docs`

## Быстрый старт

```bash
# Установка зависимостей
poetry install

# Запуск локально
poetry run uvicorn src.main:app --reload
