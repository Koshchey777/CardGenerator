from PIL import Image, ImageDraw, ImageFont
import io
import os
from utils.color_utils import hex_to_rgb, get_contrast_color_rgb


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> str:
    """
    Разбивает длинный текст на строки.
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def generate_quote_card(
        quote: str,
        author: str = "",
        username: str = "",
        background_color: str = "#ffffff",
        text_color: str = "auto",  # ← Изменили: теперь по умолчанию "auto"
        accent_color: str = "#667eea",
        width: int = 1200,
        height: int = 630
) -> bytes:
    """
    Генерирует минималистичную карточку с цитатой.

    Args:
        quote: Текст цитаты
        author: Имя автора (опционально)
        username: Username автора (опционально, например "ivan_dev")
        background_color: Цвет фона в HEX
        text_color: Цвет текста в HEX или "auto" для автоматического контраста
        accent_color: Акцентный цвет (кавычки, линия) в HEX
        width: Ширина изображения
        height: Высота изображения
    """
    # 1. Конвертируем HEX в RGB
    bg_rgb = hex_to_rgb(background_color)
    accent_rgb = hex_to_rgb(accent_color)

    # Определяем цвет текста (авто-контраст или заданный)
    if text_color == "auto":
        text_rgb = get_contrast_color_rgb(background_color)
    else:
        text_rgb = hex_to_rgb(text_color)

    # 2. Создаем фон
    image = Image.new('RGB', (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(image)

    # 3. Загружаем шрифты
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        font_quote = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Regular.ttf"),
            56
        )
        font_author = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Bold.ttf"),
            36
        )
    except IOError:
        font_quote = ImageFont.load_default()
        font_author = ImageFont.load_default()

    # Отступы
    margin_x = 150
    max_text_width = width - (margin_x * 2)

    # 4. Рисуем декоративные кавычки сверху
    quote_mark_y = 150
    quote_size = 80
    quote_gap = 20

    # Левая кавычка
    draw.rectangle(
        [(width // 2 - quote_size - quote_gap // 2, quote_mark_y),
         (width // 2 - quote_gap // 2, quote_mark_y + quote_size)],
        fill=accent_rgb
    )

    # Правая кавычка
    draw.rectangle(
        [(width // 2 + quote_gap // 2, quote_mark_y),
         (width // 2 + quote_size + quote_gap // 2, quote_mark_y + quote_size)],
        fill=accent_rgb
    )

    # 5. Рисуем текст цитаты (с переносом)
    quote_y = quote_mark_y + quote_size + 80
    wrapped_quote = wrap_text(quote, font_quote, max_text_width, draw)

    # Измеряем блок цитаты
    quote_bbox = draw.multiline_textbbox((0, 0), wrapped_quote, font=font_quote)
    quote_width = quote_bbox[2] - quote_bbox[0]
    quote_height = quote_bbox[3] - quote_bbox[1]

    # Центрируем цитату
    quote_x = (width - quote_width) / 2

    draw.multiline_text(
        (quote_x, quote_y),
        wrapped_quote,
        fill=text_rgb,  # ← Используем авто-контрастный цвет
        font=font_quote,
        align="center"
    )

    # 6. Рисуем разделительную линию (если есть автор)
    if author or username:
        line_y = quote_y + quote_height + 60
        line_width = 100
        line_x = (width - line_width) / 2

        draw.rectangle(
            [(line_x, line_y), (line_x + line_width, line_y + 3)],
            fill=accent_rgb
        )

        # 7. Рисуем подпись автора
        author_text = ""
        if author:
            author_text += f"— {author}"
        if username:
            if author_text:
                author_text += "  "
            author_text += f"@{username}"

        # Измеряем текст автора
        author_bbox = draw.textbbox((0, 0), author_text, font=font_author)
        author_width = author_bbox[2] - author_bbox[0]
        author_height = author_bbox[3] - author_bbox[1]

        author_x = (width - author_width) / 2
        author_y = line_y + 40

        draw.text(
            (author_x, author_y),
            author_text,
            fill=text_rgb,  # ← Используем тот же цвет, что и цитата
            font=font_author
        )

    # 8. Сохраняем в буфер
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()