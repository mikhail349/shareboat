class AssetFileCountException(Exception):
    pass

class FileSizeException(Exception):
    def __init__(self, msg='Размер файла превышает 5 МБ', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)