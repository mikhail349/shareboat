class AssetFileCountException(Exception):
    pass

class FileSizeException(Exception):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(f'Размер файла превышает {msg} МБ', *args, **kwargs)