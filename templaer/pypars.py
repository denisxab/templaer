import os
import re
import sys
import typing
import pathlib

""" 
Шаблон командной строки:

Позиционный1 Позиционный2 -Флаг2_ -Флаг2_ -Именованный1 Значение1 Значение2 -Именованный1 Значение1 Значение2
"""


class TArgs(typing.NamedTuple):
    # Текущий путь
    in_path: str
    # Позиционные аргументы, те что не начинаются на `-Символы`
    position_args: list[str]
    # Именованные аргументы, те что начинаются на `-Символы`
    named_args: dict[str, str]
    # Флаги, те что начинаются на `-Символы_`
    flags: list[str]


def toBash(argv: list[str] | None = None) -> str:
    """
    Распарсить строку на наличие аргументов и флагов.

    argv: Список аргументов, если не передан то возьмется `sys.argv`

    Простой пример:
    >>> ~py Путь.py "КоманднаяСтрокаДляПарсинга"
    Большой пример:
    >>> ~py py/pypars.py "-rsync-delete-server-folder ./firebird_book1 root@5.63.154.238:/home/ubuntu/test 80 -ess md ms  -p 1010 asd a22 -d_ -W_ -dfc_" 
    """
    if argv is None:
        argv = sys.argv
    # Аргументы командной строки в нормальном виде
    targs: TArgs = parse_args(in_path=argv[0], argv=argv[1].split())
    ##
    # Итоговая команда
    ##
    res_command = []
    #
    # Формируем флаги
    #
    if targs.flags:
        res_command.append("local _f=({f})".format(
            f=' '.join(
                [f'"{x}"' for x in targs.flags]
            ))
        )
    #
    # Формируем позиционные аргументы
    #
    res_command.append("local _p=({f})".format(f=' '.join(
        [f'"{x}"' for x in targs.position_args]
    )))
    #
    # Формируем именованные аргументы
    #
    for k, v in targs.named_args.items():
        res_command.append("local {k}=({f})".format(
            k=k, f=' '.join([f'"{x}"' for x in v]))
        )
    return ';\n'.join(res_command)+';'


def parse_args(in_path: str, argv: list[str]):
    #
    # Получить флаги
    #
    flags = []
    for i, x in enumerate(argv):
        if (r := re.search("-([\w\d]+)_", x)):
            flags.append(r.group(1))
            argv[i] = None
    #
    # Получить именованные аргументы
    #
    last_key = []
    named_args = {}
    for i, x in enumerate(argv):
        if not x:
            continue
        # Берем название ключа
        if (r := re.search("\A-([\w\d]+)(?!_)\Z", x)):
            last_key = r.group(1)
            named_args[last_key] = []
            argv[i] = None
            continue
        # Прекращаем добавлять массив значения если значение началось на `-`
        if x.startswith("-"):
            last_key = None
            continue
        # Добавляем значение в ключ
        if last_key:
            named_args[last_key].append(x)
            argv[i] = None
    #
    # Получить позиционные аргументы
    #
    position_args = [x for x in argv if x]
    return TArgs(in_path=in_path, flags=flags, named_args=named_args, position_args=position_args)


def files_from_path(path: str | pathlib.Path, regex: str):
    """
    Получить всей файлы в указанной директории с учетом вложенности

    path: Путь к папке 
    """

    # Проходим рекурсивно по всем поддиректориям и файлам внутри них
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            # Проверяем на соответствие указному шаблону
            if re.search(regex, filename):
                # Получаем полный путь к файлу
                yield os.path.join(dirpath, filename)


# Сразу выполняем парсинг командной строки при импорте модуля
# print(toBash())
