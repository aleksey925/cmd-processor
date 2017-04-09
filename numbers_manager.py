import os
import sys
import logging

import commands
import plugins.nums_manager

from cmd.cmd import CommandProcessor
from command_container import CommandContainer


def execute_command_file(manage_numbers: CommandProcessor, commands: str):
    """
    Выполняет команды из скрипта.
    :param manage_numbers: экземпляр CommandProcessor
    :param commands: команды из скрипта в строковом представлении 
    """
    for row_num, raw_command in enumerate(commands.split('\n')):
        try:
            manage_numbers.execute(raw_command)
        except Exception as err:
            print(f'Произошла ошибка при выполнении скрипта:\n'
                  f'Строка {row_num + 1}, команда "{raw_command}"')
            logging.getLogger('main').exception(err)
            exit(1)
    print('Выполнение программы успешно завершено')


nums_managers = CommandProcessor(CommandContainer)
nums_managers.start_massage = (
    'Добро пожаловать в программу управляющую набором целых чисел.\nДля '
    'получения справки наберите команду help.'
)

if len(sys.argv) != 1:
    path = os.path.abspath(sys.argv[1])
    if not os.path.exists(path):
        print(f'Немогу найти указанный файл, проверьте путь: {path}')
        exit(1)

    try:
        with open(path, encoding='utf8') as file_:
            execute_command_file(nums_managers, file_.read())
        exit(0)
    except UnicodeDecodeError:
        print('Конвертируйте файл в utf8. Другие кодировки не '
              'поддерживваются.')

nums_managers.loop()
