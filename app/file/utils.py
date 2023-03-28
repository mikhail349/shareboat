import logging
import uuid

logger = logging.getLogger(__name__)


def get_file_path(instance, filename, path='') -> str:
    """Получить путь файла для сохранения.

    Returns:
        str: путь файла

    """
    return '%s%s.%s' % (path, uuid.uuid4(),  'webp')


def limit_size(
    width: int,
    height: int,
    max_width: int = 1920,
    max_height: int = 1080
) -> tuple[int, int]:
    """Ограничить размер файла, сохраняя пропорции.

    Args:
        width: ширина
        height: высота
        max_width: макс ширина, до которой надо ограничить
        max_height: макс высота, до которой надо ограничить

    Returns:
        tuple[int, int]: новая ширина, новая высота

    """
    while width > max_width or height > max_height:
        if width > max_width:
            height = round(max_width / width * height)
            width = max_width
        if height > max_height:
            width = round(max_height / height * width)
            height = max_height

    return width, height
