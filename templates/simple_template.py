from PIL import Image, ImageDraw, ImageFont
import io
import os
from utils.color_utils import hex_to_rgb, get_contrast_color_rgb


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> str:
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


def generate_simple_card(
        title: str,
        background_color: str = "#1a1a2e",
        text_color: str = "auto"
) -> bytes:
    width, height = 1200, 630

    bg_rgb = hex_to_rgb(background_color)

    if text_color == "auto":
        text_rgb = get_contrast_color_rgb(background_color)
    else:
        text_rgb = hex_to_rgb(text_color)

    image = Image.new('RGB', (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(image)

    font_size = 72
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        font = ImageFont.truetype(
            os.path.join(current_dir, "fonts", "Inter_28pt-Bold.ttf"),
            font_size
        )
    except IOError:
        font = ImageFont.load_default()

    max_text_width = width - 200

    wrapped_title = wrap_text(title, font, max_text_width, draw)

    bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # Рисуем текст
    draw.multiline_text(
        (x, y),
        wrapped_title,
        fill=text_rgb,
        font=font,
        align="center"
    )

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()