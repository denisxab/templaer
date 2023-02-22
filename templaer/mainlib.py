import re
import json
import pathlib
from jinja2 import Template
from .pypars import files_from_path, parse_args, TArgs
from .helper import color, log


def build_conf(template_str: str, context: dict[str, str]) -> str:
    """Собрать текст из шаблона и контекста

    param template_str: Шаблонный текст
    param context: Ключи и значения шаблона
    return: Собранный тест
    """
    template: Template = Template(template_str)
    config_file = template.render(context)
    return config_file


def save_tpl_file(in_file: str, write_text: str):
    """Сохранить собранный текст в новый файл(без окончания на `.tpl`) 

    :param in_file: Исходный файл с окончанием на `.tpl`
    :param write_text: Собранный шаблонный текст
    """
    # Обрезать `.tpl` с конца имени файла
    path_save = re.sub('\.tpl\Z', '', in_file)
    # Сохранить текст в новый файл
    pathlib.Path(path_save).write_text(write_text)
    log(f'{color.green.value}Build:{color.reset.value}\t{path_save}')


def main(argv: list[str]):
    """
Templaer - универсальный CLI шаблонизатор конфигурационных файлов, основанный на Jinja2.

* GitHub    = https://github.com/denisxab/templaer
* Pip       = https://pypi.org/project/templaer/
* Habr      = https://habr.com/ru/post/717996/

Описание CLI:

-c Путь_context.json                = Указать путь к файлу, из которого будут браться данными для шаблонов.
-f Файл0 Файл1                      = Указать конкретные файлы, с расширением `.tpl`.
-d ПутьДиректории0 ПутьДиректории1  = Указать путь к директории, в которой будут искаться все файлы с расширением `.tpl`.
-e_                                 = Если указа этот флаг то также создастся `.env` файл, в те же папки где есть файлы `.tpl`

    """

    context: dict[str, str] = {}
    cli_args: TArgs = parse_args(
        argv[0],
        argv[1:],
    )
    # Список директорий в которых есть шаблонные файлы
    use_paths_dirs = set()
    ##
    # Ели не переданы ни каких данных то выводим документацию по CLI
    ##
    if len(argv) == 1:
        log(main.__doc__)
        return
    ###
    # Получаем данные для шаблона
    ##
    path_to_context: pathlib.Path
    context: dict | list = {}
    if path_to_context := cli_args.named_args.get('c'):
        path_to_context = pathlib.Path(path_to_context[0])
        context = json.loads(path_to_context.read_text())
    else:
        raise KeyError("Не указан путь к `context.json`")
    ##
    # Собираем шаблоны для указанных файлов
    ##
    if path_to_templates := cli_args.named_args.get('f'):
        # Перебираем файлы
        for _files in path_to_templates:
            template_str: str = pathlib.Path(_files).resolve().read_text()
            build_text: str = build_conf(template_str, context)
            save_tpl_file(_files, build_text)
            # Добавить папку в используемые
            use_paths_dirs.add(pathlib.Path(_files).parent.resolve())
    ##
    # Находим файлы которые оканчиваются на `.tpl`, в указанной директории. И собираем шаблон
    ##
    if path_to_dir := cli_args.named_args.get('d'):
        # Перебираем папки
        for _dirs in path_to_dir:
            # Перебираем файлы
            for _files in files_from_path(pathlib.Path(_dirs).resolve(), '.*\.tpl'):
                template_str: str = pathlib.Path(_files).resolve().read_text()
                build_text: str = build_conf(template_str, context)
                save_tpl_file(_files, build_text)
                # Добавить папку в используемые
                use_paths_dirs.add(pathlib.Path(_files).parent.resolve())
    ###
    # Если нужно, то создаем env файл
    ##
    if 'e' in cli_args.flags:
        # Если контекст в типе словарь
        if type(context) == dict:
            # То конвертируем словарь в строку для .env файлов
            write_text = []
            for k, v in context.items():
                if type(v) == str:
                    write_text.append(f'{k}="{v}"')
                else:
                    write_text.append(f'{k}={v}')
            # for _path in use_paths_dirs:
            # Записываем в файл `.env` в туже папку где `context.json`
            (path_to_context.parent / '.env').write_text(
                '\n'.join(write_text)
            )
