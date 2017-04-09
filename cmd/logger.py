import logging


def create_logger(path: str) -> logging.Logger:
    """
    Создает логгер для проекта
    :argument path: путь к log файлу
    """
    log = logging.getLogger('main')
    log.setLevel(logging.DEBUG)

    # Определяется формат логов и добавляется к обработчику
    file_formatter = logging.Formatter(
        ('#%(levelname)-s, [%(asctime)s], %(pathname)s, line %(lineno)d: '
         '%(message)s'), datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Создаётся обработчик,который будет писать сообщения в файл
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # добавляем обработчики в _logger
    log.addHandler(file_handler)

    return log
