"""
Модуль с плагинами
"""
import os

from cmd import command, Arg
from command_container import CommandContainer
from storage import NumbersStorage


class NumsAdditionalCommands(NumbersStorage, CommandContainer):
    @staticmethod
    @command('sort', 'устанавливает значение в указанную позицию',
             Arg('mode', str, 'asc', choices=('asc', 'desc')))
    def sort(mode: str):
        if mode == 'asc':
            NumsAdditionalCommands.storage.sort()
        else:
            NumsAdditionalCommands.storage.sort(reverse=True)

    @staticmethod
    @command('save', 'сохраняет набор в файл с заданным именем форматом',
             Arg('path', str, required=True),
             Arg('format_file', str, required=True, choices=('txt', 'html')),
             Arg('separator', str, '\t'))
    def save(path, format_file, separator):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Сохраненные данные</title>
</head>
<body>
    <div>{separator.join(map(str, NumsAdditionalCommands.storage))}</div>
</body>
</html>
                """
        path = os.path.abspath(path)
        try:
            with open(path, 'w', encoding='utf8') as out:
                if format_file == 'txt':
                    out.write(
                        separator.join(map(str, NumsAdditionalCommands.storage))
                    )
                else:
                    out.write(html)
        except FileNotFoundError:
            print(f'Отсуствует файл или дирректория: {path}')
