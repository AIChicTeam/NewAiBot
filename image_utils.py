import os
import shutil
from PIL import Image

def crop_center(image: Image.Image, target_aspect: float) -> Image.Image:
    """
    Обрезает изображение по центру под нужное соотношение сторон.
    """
    width, height = image.size
    current_aspect = width / height

    if current_aspect > target_aspect:
        # Обрезаем по ширине
        new_width = int(height * target_aspect)
        left = (width - new_width) // 2
        right = left + new_width
        return image.crop((left, 0, right, height))
    else:
        # Обрезаем по высоте
        new_height = int(width / target_aspect)
        top = (height - new_height) // 2
        bottom = top + new_height
        return image.crop((0, top, width, bottom))

def determine_target_size(image: Image.Image):
    """
    Определяет целевой размер и аспект (соотношение сторон).
    Возвращает кортеж: (размер, аспект)
    """
    width, height = image.size
    aspect_ratio = width / height

    if 0.85 <= aspect_ratio <= 1.15:
        return (1024, 1024), 1.0  # Почти квадрат
    else:
        return (832, 1216), 832 / 1216  # Вертикальное фото

def resize_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """
    Масштабирует изображение под указанный размер.
    """
    return image.resize(size, Image.LANCZOS)

def clear_output_folder(folder: str):
    """
    Очищает папку (полностью удаляет и создаёт заново).
    """
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
