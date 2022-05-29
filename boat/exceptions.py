class BoatFileCountException(Exception):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(f'Можно приложить не более {msg} фотографий', *args, **kwargs)

class PriceDateRangeException(Exception):
    def __init__(self, msg='Выбранный период содержит недоступные даты', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
