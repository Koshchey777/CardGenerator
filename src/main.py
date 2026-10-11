from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from templates.simple_template import generate_simple_card
from templates.gradient_template import generate_gradient_card
from templates.magazine_template import generate_magazine_card
from templates.quote_template import generate_quote_card
from utils.cache_utils import generate_cache_key, get_cached_image, save_to_cache, clean_expired_cache, get_cache_stats


app = FastAPI(
    title="Fast OG Card Generator",
    description="API для генерации социальных карточек (Open Graph images)",
    version="0.3.0"
)


class SimpleCardRequest(BaseModel):
    title: str = Field(..., description="Текст заголовка")
    background_color: str = Field(default="#1a1a2e", description="Цвет фона в HEX")
    text_color: str = Field(default="#ffffff", description="Цвет текста в HEX")


class GradientCardRequest(BaseModel):
    title: str = Field(..., description="Текст заголовка")
    author: str = Field(default="", description="Имя автора (опционально)")
    date: str = Field(default="", description="Дата публикации (опционально)")
    background_color: str = Field(default="#667eea", description="Основной цвет градиента в HEX")
    text_color: str = Field(default="auto", description="Цвет текста в HEX или 'auto'")
    size: str = Field(default="twitter", description="Размер: twitter, facebook, instagram, linkedin")


class MagazineCardRequest(BaseModel):
    category: str = Field(..., description="Категория/тег (например, 'PYTHON', 'TECH')")
    title: str = Field(..., description="Основной заголовок")
    issue_number: str = Field(default="", description="Номер выпуска (опционально)")
    date: str = Field(default="", description="Дата (опционально)")
    background_color: str = Field(default="#14141e", description="Цвет фона в HEX")
    accent_color: str = Field(default="auto", description="Акцентный цвет в HEX или 'auto'")
    text_color: str = Field(default="auto", description="Цвет текста в HEX или 'auto'")
    size: str = Field(default="twitter", description="Размер: twitter, facebook, instagram, linkedin")


class QuoteCardRequest(BaseModel):
    quote: str = Field(..., description="Текст цитаты")
    author: str = Field(default="", description="Имя автора (опционально)")
    username: str = Field(default="", description="Username автора (опционально)")
    background_color: str = Field(default="#ffffff", description="Цвет фона в HEX")
    text_color: str = Field(default="auto", description="Цвет текста в HEX или 'auto'")
    accent_color: str = Field(default="#667eea", description="Акцентный цвет (кавычки, линия) в HEX")
    size: str = Field(default="twitter", description="Размер: twitter, facebook, instagram, linkedin")

SIZES = {
    "twitter": (1200, 675),
    "facebook": (1200, 630),
    "instagram": (1080, 1080),
    "linkedin": (1200, 627)
}


@app.get("/")
def root():
    return {"message": "Fast OG Card Generator is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/generate/simple")
def generate_simple(request: SimpleCardRequest):
    """
    Генерирует простую карточку с текстом на сплошном фоне.
    """
    try:
        # 1. Создаем параметры для хэша
        cache_params = {
            "template": "simple",
            "title": request.title,
            "background_color": request.background_color,
            "text_color": request.text_color
        }

        # 2. Генерируем хэш
        cache_key = generate_cache_key(cache_params)

        # 3. Проверяем кэш
        cached_image = get_cached_image(cache_key)
        if cached_image:
            # Возвращаем из кэша (быстро!)
            return Response(
                content=cached_image,
                media_type="image/png",
                headers={
                    "Content-Disposition": "inline; filename=card.png",
                    "X-Cache": "HIT"  # ← Заголовок для отладки
                }
            )

        # 4. Генерируем новое изображение
        image_bytes = generate_simple_card(
            title=request.title,
            background_color=request.background_color,
            text_color=request.text_color
        )

        # 5. Сохраняем в кэш
        save_to_cache(cache_key, image_bytes)

        # 6. Возвращаем с заголовком MISS
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=card.png",
                "X-Cache": "MISS"  # ← Заголовок для отладки
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@app.post("/generate/gradient")
def generate_gradient(request: GradientCardRequest):
    """
    Генерирует карточку с градиентным фоном.
    """
    try:
        width, height = SIZES.get(request.size, (1200, 630))

        # Параметры для хэша
        cache_params = {
            "template": "gradient",
            "title": request.title,
            "author": request.author,
            "date": request.date,
            "background_color": request.background_color,
            "text_color": request.text_color,
            "size": request.size
        }

        cache_key = generate_cache_key(cache_params)
        cached_image = get_cached_image(cache_key)

        if cached_image:
            return Response(
                content=cached_image,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=card_{request.size}.png",
                    "X-Cache": "HIT"
                }
            )

        image_bytes = generate_gradient_card(
            title=request.title,
            author=request.author,
            date=request.date,
            background_color=request.background_color,
            text_color=request.text_color,
            width=width,
            height=height
        )

        save_to_cache(cache_key, image_bytes)

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=card_{request.size}.png",
                "X-Cache": "MISS"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@app.post("/generate/magazine")
def generate_magazine(request: MagazineCardRequest):
    """
    Генерирует карточку в стиле обложки журнала.
    """
    try:
        width, height = SIZES.get(request.size, (1200, 630))

        cache_params = {
            "template": "magazine",
            "category": request.category,
            "title": request.title,
            "issue_number": request.issue_number,
            "date": request.date,
            "background_color": request.background_color,
            "accent_color": request.accent_color,
            "text_color": request.text_color,
            "size": request.size
        }

        cache_key = generate_cache_key(cache_params)
        cached_image = get_cached_image(cache_key)

        if cached_image:
            return Response(
                content=cached_image,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=card_magazine_{request.size}.png",
                    "X-Cache": "HIT"
                }
            )

        image_bytes = generate_magazine_card(
            category=request.category,
            title=request.title,
            issue_number=request.issue_number,
            date=request.date,
            background_color=request.background_color,
            accent_color=request.accent_color,
            text_color=request.text_color,
            width=width,
            height=height
        )

        save_to_cache(cache_key, image_bytes)

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=card_magazine_{request.size}.png",
                "X-Cache": "MISS"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@app.post("/generate/quote")
def generate_quote(request: QuoteCardRequest):
    """
    Генерирует минималистичную карточку с цитатой.
    """
    try:
        width, height = SIZES.get(request.size, (1200, 630))

        cache_params = {
            "template": "quote",
            "quote": request.quote,
            "author": request.author,
            "username": request.username,
            "background_color": request.background_color,
            "text_color": request.text_color,
            "accent_color": request.accent_color,
            "size": request.size
        }

        cache_key = generate_cache_key(cache_params)
        cached_image = get_cached_image(cache_key)

        if cached_image:
            return Response(
                content=cached_image,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=card_quote_{request.size}.png",
                    "X-Cache": "HIT"
                }
            )

        image_bytes = generate_quote_card(
            quote=request.quote,
            author=request.author,
            username=request.username,
            background_color=request.background_color,
            text_color=request.text_color,
            accent_color=request.accent_color,
            width=width,
            height=height
        )

        save_to_cache(cache_key, image_bytes)

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=card_quote_{request.size}.png",
                "X-Cache": "MISS"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@app.get("/cache/stats")
def cache_statistics():
    """
    Возвращает статистику кэша.
    """
    return get_cache_stats()


@app.post("/cache/clean")
def clean_cache():
    """
    Очищает устаревшие файлы из кэша.
    """
    cleaned = clean_expired_cache()
    return {"message": f"Удалено устаревших файлов: {cleaned}"}