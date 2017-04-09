class NoSuchCommand(Exception):
    def __init__(self, command):
        self.args = (f'Команды {command} не существует',)
