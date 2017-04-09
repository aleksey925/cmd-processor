import re

from itertools import zip_longest
from os.path import join, abspath, dirname, split

from .logger import create_logger
from .exceptions import NoSuchCommand

__all__ = [
    'Arg',
    'Command',
    'command',
    'ContainerMeta'
]

LOGGER = create_logger(join(split(abspath(dirname(__file__)))[0], 'log.txt'))


class Arg:
    """
    Представляет аргумент команды. Экземпляр хранит в себе переданное
    пользователем значение и правила для проверки его валидности.
    """
    replacement_table = {
        '\s': ' ',
        r'\t': '\t',
        '\\\\': '\\'
    }

    def __init__(self, name, type_, default=None, required=False,
                 choices=tuple()):
        self.name = name
        self.required = required
        self.type_ = type_
        self.choices = choices
        self.default = default

        self.value = None

    def __call__(self, raw_data):
        """
        Позволяет вызывать экземпляр класса как функцию. При вызове запускает 
        валидацию данных
        :param raw_data: данные, которые нужно провалидировать и сконвертировать 
        """
        if raw_data == '' and self.default is not None:
            self.value = self.default
            return
        if raw_data == '' and self.required is True:
            raise ValueError(f'Пропущен обязательный аргумент {self.name}')
        if self.choices:
            if raw_data not in self.choices:
                raise ValueError(
                    f'Аргумент должен иметь 1 из перечисленных далее значений:'
                    f' {", ".join(self.choices)}'
                )
        if raw_data == '':
            return

        try:
            self.value = self.type_(self._replace_escaped_seq(raw_data))
        except ValueError:
            raise ValueError(
                f'Невозможно преобразовать "{raw_data}" в '
                f'{self.type_.__name__}'
            )

    def _replace_escaped_seq(self, data: str):
        for old, new in self.replacement_table.items():
            data = data.replace(old, new)
        return data

    def __str__(self):
        return (f'<Arg(name={self.name}, type_={self.type_.__name__}, '
                f'required={self.required}, choices={self.choices}, '
                f'default={self.default})>')

    def __repr__(self):
        return self.__str__()


class Command:
    """
    Представляет зарегистрированные в программе команды.
    """
    def __init__(self, action, name, descr='', *args):
        self.name = name
        self.action = action
        self.descr = descr
        self.args = args

    def __call__(self, raw_args, *args, **kwargs):
        """
        Позволяет вызывать экземпляр класса как функцию.
        При вызове запускает проверку аргументов и выполнение команды.
        :param raw_args: аргументы (до их интерпретации) с которыми должна
         выполниться команда 
        """
        self._validate(raw_args)
        self.action(*[i.value for i in self.args if i.value is not None])

    def _validate(self, raw_args):
        """
        Проверяет соответствуют ли аргументы заданным правилам
        :param raw_args: аргументы для проверки
        """
        if len(raw_args) > len(self.args):
            raise ValueError(
                f'Переданно {len(raw_args)} аргументов, ожидалось '
                f'{len(self.args)}'
            )

        for arg, raw_arg in zip_longest(self.args, raw_args, fillvalue=''):
            arg(raw_arg)

    def __str__(self):
        return f'<Command name={self.name}>'


def command(name, descr='', *args):
    """
    Декоратор для создания команды
    :param name: название команды
    :param descr: описание команды
    :param args: аргументы, которые принимает команда
    :return: обертка возвращающая при вызове экземпляр класса Command 
    """
    def wrapper(func):
        return Command(func, name, descr, *args)

    return wrapper


class ContainerMeta(type):
    """ 
    Метакласс, который отыскивает в дочерних классах все методы обернутые 
    декоратором command и регистрирует их в атрибуте commands 
    """
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'commands'):
            cls.commands = {
                'exit': command('exit', descr='завершает работу программы')(
                    exit
                ),
                'help': command('help', descr='выводит справку о командах')(
                    lambda: ContainerMeta.help_(cls)
                )
            }
        else:
            cls.register_commands(attrs)

        super(ContainerMeta, cls).__init__(name, bases, attrs)

    def register_commands(cls, attrs):
        for attr in attrs:
            attr = getattr(cls, attr, None)
            try:
                cls.commands[attr.name] = attr
            except AttributeError:
                continue

    @staticmethod
    def help_(command_container):
        print('Список поддерживаемых команд: ')
        for command_ in command_container.commands.values():
            doc = command_.descr if command_.descr else 'Описание недоступно'
            print(f'\t{command_.name} - {doc}')


class CommandProcessor:
    """
    Базовый класс для построения консольного приложения, которое будет 
    запрашивать ввод команд для управления.
    """
    start_massage = 'Для получения справки введите команду help'
    prompt = '> '

    def __init__(self, command_container):
        self.command_container = command_container

    def get_command(self, name) -> Command:
        """
        Извлекает команду из глобального храшилища 
        :param name: имя команды 
        :return: экземпляр класса Command
        """
        try:
            command_ = self.command_container.commands[name]
        except KeyError:
            raise NoSuchCommand(name)
        return command_

    def parsing_command(self, raw_command):
        """
        Разбирает введеную пользователем команду
        :param raw_command: введенная пользователем строка 
        :return:
        """
        raw_command = raw_command.strip()
        raw_command = re.split('\s+', raw_command)
        if raw_command:
            raw_command[0] = raw_command[0].lower()
            command_ = self.get_command(raw_command[0])
            return command_, raw_command[1:]

    def execute(self, raw_command):
        command_, args = self.parsing_command(raw_command)
        command_(args)

    def loop(self):
        """
        Запускает бесконечный цикл обрабатыващий ввод и команд и 
        их интерпретацию
        """
        print(self.start_massage)
        while True:
            raw_command = input(self.prompt)
            try:
                self.execute(raw_command)
            except NoSuchCommand as err:
                self.print_error(err)
                continue
            except ValueError as err:
                self.print_error(err)
            except Exception as err:
                LOGGER.exception(err)
                print(
                    'Возникла непрдвиденная ошибка. Подробная информация '
                    'записана в лог файл.'
                )

    @staticmethod
    def print_error(error: Exception):
        print(' '.join(error.args))
