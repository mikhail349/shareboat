class BookingDateRangeException(Exception):
    """Исключение бронирования лодки - даты заняты."""
    def __init__(self,
                 msg='Бронирование лодки на указанный период недоступно',
                 *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class BookingDuplicatePendingException(Exception):
    """Исключение бронирования лодки - повторная бронь."""
    def __init__(self, msg='Вы уже подали бронь на указанный период',
                 *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
