import enum


class color(enum.Enum):
    reset = '\x1b[0m'
    #################
    green = '\x1b[92m'
    yellow = '\x1b[93m'
    read = '\x1b[31m'
    # Рамка
    frame = '\x1b[51m'


def log(text: str):
    print(text)
