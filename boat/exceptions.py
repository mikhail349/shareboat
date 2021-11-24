class BoatFileCountException(Exception):
    def __init__(self, msg='Можно приложить не более 10 фотографий', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

class PriceDateRangeException(Exception):
    def __init__(self, msg='Выбранный период содержит недоступные даты', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
