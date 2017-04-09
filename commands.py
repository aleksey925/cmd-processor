import os
import logging

from collections import OrderedDict

from cmd import command
from cmd.cmd import Arg
from command_container import CommandContainer
from storage import NumbersStorage


class NumsBasicCommands(NumbersStorage, CommandContainer):
    @staticmethod
    @command('list',
             'выводит содержимое на экран через заданный разделеитель',
             Arg('separator', str, '\t'))
    def list(separator: str):
        print(f'{separator}'.join(map(str, NumbersStorage.storage)))

    @staticmethod
    @command('clear', descr='удаляет все из набора')
    def clear():
        NumsBasicCommands.storage.clear()

    @staticmethod
    @command('add', 'Добавляет значение в набор',
             Arg('value', int, required=True))
    def add(value: int):
        NumsBasicCommands.storage.append(value)

    @staticmethod
    @command('del', 'Удаляет из набора заданный элемент или элементы в '
                    'указанном диопазоне',
             Arg('start_index', int, required=True), Arg('stop_index', int))
    def del_(start: int, stop: int):
        if stop is None:
            del NumsBasicCommands.storage[start]
        else:
            del NumsBasicCommands.storage[slice(start, stop)]

    @staticmethod
    @command('find', 'выполняет поиск значения в наборе',
             Arg('value', int, required=True))
    def find(value: int):
        try:
            index = NumsBasicCommands.storage.index(value)
            print(f'Значение {value} найдено в позиции {index}')
        except ValueError:
            print(f'Значение {value} не найдено')

    @staticmethod
    @command('set', 'устанавливает значение в указанную позицию',
             Arg('index', int, required=True),
             Arg('value', int, required=True))
    def set(index: int, value: int):
        NumsBasicCommands.storage.insert(index, value)

    @staticmethod
    @command('get', 'читает значение в указанной позиции',
             Arg('index', int, required=True))
    def get(index: int):
        try:
            print(
                f'В позиции {index} находится значение '
                f'{NumsBasicCommands.storage[index]}'
            )
        except IndexError:
            print(f'По индексу {index} значение ещё не добавлено')

    @staticmethod
    @command('unique', 'удаляет дубликаты в наборе')
    def unique():
        NumsBasicCommands.storage = list(
            OrderedDict.fromkeys(NumsBasicCommands.storage)
        )

    @staticmethod
    @command('load', 'загружает набор из текстового файла',
             Arg('path', str, required=True), Arg('separator', str, '\t'))
    def load(path: str, separator: str):
        if os.path.exists(path):
            try:
                with open(path, encoding='utf8') as inp:
                    NumsBasicCommands.storage.extend(
                        map(int, inp.read().split(separator))
                    )
            except ValueError:
                print('Указан неправильный разделитель или файл содержит не '
                      'только цифры')
            except Exception as err:
                logging.getLogger('main').exception(err)
                print('При загрузке файла возникла ошибка')
        else:
            print('Такого файла не существует')

    @staticmethod
    @command('count', 'отображает количество чисел в наборе')
    def count():
        print(len(NumsBasicCommands.storage))
