from PIL import Image, ImageDraw, ImageFont
import io
import os
from utils.color_utils import hex_to_rgb, get_contrast_color_rgb


def create_gradient(width: int, height: int, color_start: tuple, color_end: tuple) -> Image.Image:
    """
    Создает изображение с вертикальным градиентом.

    Args:
        width: Ширина изображения
        height: Высота изображения
        color_start: Начальный цвет (RGB кортеж, например (102, 126, 234))
        color_end: Конечный цвет (RGB кортеж, например (118, 75, 162))

    Returns:
        Изображение с градиентом
    """
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / height

        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)

        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return image


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


def generate_gradient_card(
        title: str,
        author: str = "",
        date: str = "",
        background_color: str = "#667eea",  # ← Новый параметр: основной цвет фона
        text_color: str = "auto",  # ← Новый параметр: "auto" или HEX
        width: int = 1200,
        height: int = 630
) -> bytes:
    """
    Генерирует карточку с градиентным фоном, заголовком и подписью автора.

    Args:
        title: Заголовок статьи
        author: Имя автора (опционально)
        date: Дата публикации (опционально)
        background_color: Основной цвет градиента в HEX (например, "#667eea")
        text_color: Цвет текста в HEX или "auto" для автоматического контраста
        width: Ширина изображения
        height: Высота изображения
    """
    bg_start_rgb = hex_to_rgb(background_color)

    bg_end_rgb = tuple(max(0, c - 40) for c in bg_start_rgb)

    gradient = create_gradient(width, height, bg_start_rgb, bg_end_rgb)
    draw = ImageDraw.Draw(gradient)

    if text_color == "auto":
        text_rgb = get_contrast_color_rgb(background_color)
        accent_rgb = text_rgb  # Линия и акценты того же цвета, что и текст
    else:
        text_rgb = hex_to_rgb(text_color)
        accent_rgb = tuple(max(0, c - 30) for c in text_rgb)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        font_bold = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Bold.ttf"),
            72
        )
        font_regular = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Regular.ttf"),
            36
        )
    except IOError:
        font_bold = ImageFont.load_default()
        font_regular = ImageFont.load_default()

    max_text_width = width - 200  # Отступы по 100px с каждой стороны
    wrapped_title = wrap_text(title, font_bold, max_text_width, draw)

    title_bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=font_bold)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]

    title_x = (width - title_width) / 2
    title_y = (height - title_height) / 2 - 50  # Смещение вверх на 50px

    draw.multiline_text(
        (title_x, title_y),
        wrapped_title,
        fill=text_rgb,  # ← Используем авто-контрастный цвет
        font=font_bold,
        align="center"
    )

    if author or date:
        line_y = title_y + title_height + 40
        line_width = 200
        line_x = (width - line_width) / 2

        draw.rectangle(
            [(line_x, line_y), (line_x + line_width, line_y + 4)],
            fill=accent_rgb
        )

        author_text = ""
        if author:
            author_text += author
        if date:
            if author_text:
                author_text += " • "
            author_text += date

        author_bbox = draw.textbbox((0, 0), author_text, font=font_regular)
        author_width = author_bbox[2] - author_bbox[0]
        author_height = author_bbox[3] - author_bbox[1]

        author_x = (width - author_width) / 2
        author_y = line_y + 30

        draw.text(
            (author_x, author_y),
            author_text,
            fill=accent_rgb,  # ← Используем тот же цвет, что и линия
            font=font_regular
        )

    buffer = io.BytesIO()
    gradient.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()