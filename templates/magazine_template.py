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


def generate_magazine_card(
        category: str,
        title: str,
        issue_number: str = "",
        date: str = "",
        background_color: str = "#14141e",  # ← Новый параметр: темный фон по умолчанию
        accent_color: str = "auto",  # ← Новый параметр: авто-контраст для акцентов
        text_color: str = "auto",  # ← Новый параметр: авто-контраст для текста
        width: int = 1200,
        height: int = 630
) -> bytes:
    """
    Генерирует карточку в стиле обложки журнала.

    Args:
        category: Категория/тег (например, "PYTHON", "TECH")
        title: Основной заголовок
        issue_number: Номер выпуска (опционально)
        date: Дата (опционально)
        background_color: Цвет фона в HEX
        accent_color: Акцентный цвет (категория, линия, полоса) в HEX или "auto"
        text_color: Цвет заголовка в HEX или "auto"
        width: Ширина изображения
        height: Высота изображения
    """
    # 1. Конвертируем цвета
    bg_rgb = hex_to_rgb(background_color)

    # Определяем цвет текста (авто-контраст или заданный)
    if text_color == "auto":
        text_rgb = get_contrast_color_rgb(background_color)
    else:
        text_rgb = hex_to_rgb(text_color)

    # Определяем акцентный цвет
    # Если "auto" — используем контрастный к фону, но не такой как текст
    # Для темного фона — яркий синий, для светлого — насыщенный синий
    if accent_color == "auto":
        # По умолчанию используем красивый синий #667eea
        accent_rgb = (102, 126, 234)
    else:
        accent_rgb = hex_to_rgb(accent_color)

    # 2. Создаем фон
    image = Image.new('RGB', (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(image)

    # 3. Загружаем шрифты
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        font_category = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Bold.ttf"),
            48
        )
        font_title = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Bold.ttf"),
            80
        )
        font_footer = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Regular.ttf"),
            32
        )
    except IOError:
        font_category = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Отступы
    margin_x = 100
    max_text_width = width - (margin_x * 2)

    # 4. Рисуем декоративную полосу сверху
    draw.rectangle(
        [(0, 0), (width, 8)],
        fill=accent_rgb
    )

    # 5. Рисуем категорию (сверху)
    category_y = 150
    category_upper = category.upper()

    draw.text(
        (margin_x, category_y),
        category_upper,
        fill=accent_rgb,  # ← Используем акцентный цвет
        font=font_category
    )

    # 6. Рисуем разделительную линию под категорией
    line_y = category_y + 70
    line_width = 150
    draw.rectangle(
        [(margin_x, line_y), (margin_x + line_width, line_y + 4)],
        fill=accent_rgb  # ← Используем акцентный цвет
    )

    # 7. Рисуем основной заголовок (с переносом)
    title_y = line_y + 60
    wrapped_title = wrap_text(title, font_title, max_text_width, draw)

    draw.multiline_text(
        (margin_x, title_y),
        wrapped_title,
        fill=text_rgb,
        font=font_title,
        align="left"
    )

    if issue_number or date:
        footer_text = ""
        if issue_number:
            footer_text += f"#{issue_number}"
        if date:
            if footer_text:
                footer_text += " • "
            footer_text += date

        footer_y = height - 150

        if text_rgb == (255, 255, 255):
            footer_rgb = (150, 150, 150)
        else:
            footer_rgb = (100, 100, 100)

        draw.text(
            (margin_x, footer_y),
            footer_text,
            fill=footer_rgb,
            font=font_footer
        )

    # 9. Сохраняем в буфер
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()