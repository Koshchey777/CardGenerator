def hex_to_rgb(hex_color: str) -> tuple:

    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def get_contrast_color(background_hex: str) -> str:
    r, g, b = hex_to_rgb(background_hex)

    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    if luminance > 0.5:
        return "#000000"
    else:
        return "#ffffff"


def get_contrast_color_rgb(background_hex: str) -> tuple:
    contrast_hex = get_contrast_color(background_hex)
    return hex_to_rgb(contrast_hex)