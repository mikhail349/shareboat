import uuid

import logging
logger = logging.getLogger(__name__)


def get_file_path(instance, filename, path=""):
    return "%s%s.%s" % (path, uuid.uuid4(),  'webp')


def limit_size(width, height, max_width=1920, max_height=1080):
    while width > max_width or height > max_height:
        if width > max_width:
            height = round(max_width / width * height)
            width = max_width
        if height > max_height:
            width = round(max_height / height * width)
            height = max_height

    return (width, height)
