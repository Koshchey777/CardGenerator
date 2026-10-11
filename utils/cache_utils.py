import hashlib
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "cache"

CACHE_TTL = 604800


def ensure_cache_dir():
    """
    Создает папку кэша, если её нет.
    """
    CACHE_DIR.mkdir(exist_ok=True)


def generate_cache_key(params: dict) -> str:
    """
    Генерирует уникальный хэш для параметров запроса.

    Args:
        params: Словарь параметров (template, title, colors, size и т.д.)

    Returns:
        Строка хэша (первые 16 символов SHA256)
    """
    sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)

    hash_object = hashlib.sha256(sorted_params.encode('utf-8'))

    return hash_object.hexdigest()[:16]


def get_cached_image(cache_key: str) -> bytes | None:
    """
    Пытается получить изображение из кэша.

    Args:
        cache_key: Хэш параметров

    Returns:
        Байты изображения, если найдено и не устарело, иначе None
    """
    ensure_cache_dir()

    file_path = CACHE_DIR / f"{cache_key}.png"

    if not file_path.exists():
        return None

    file_age = time.time() - file_path.stat().st_mtime
    if file_age > CACHE_TTL:
        # Файл устарел, удаляем его
        file_path.unlink()
        return None

    return file_path.read_bytes()


def save_to_cache(cache_key: str, image_bytes: bytes):
    """
    Сохраняет изображение в кэш.

    Args:
        cache_key: Хэш параметров
        image_bytes: Байты изображения
    """
    ensure_cache_dir()

    file_path = CACHE_DIR / f"{cache_key}.png"
    file_path.write_bytes(image_bytes)


def clean_expired_cache():
    """
    Очищает устаревшие файлы из кэша.
    Можно вызывать периодически или при старте сервера.
    """
    ensure_cache_dir()

    current_time = time.time()
    cleaned_count = 0

    for file_path in CACHE_DIR.glob("*.png"):
        file_age = current_time - file_path.stat().st_mtime
        if file_age > CACHE_TTL:
            file_path.unlink()
            cleaned_count += 1

    return cleaned_count


def get_cache_stats() -> dict:
    """
    Возвращает статистику кэша (для мониторинга).
    """
    ensure_cache_dir()

    files = list(CACHE_DIR.glob("*.png"))
    total_size = sum(f.stat().st_size for f in files)

    return {
        "total_files": len(files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "cache_dir": str(CACHE_DIR)
    }
