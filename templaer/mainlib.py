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
Templaer - универсальный CLI шаблонизатор конфигурационных файлов. Основанный на `Jinja2`.

Описание CLI:

-c Путь_context.json                = Указать путь к файлу с данными для шаблонов
-f Файл0 Файл1                      = Указать конкретные файлы для шаблонизатор
-d ПутьДиректории0 ПутьДиректории1  = Указать путь в котором будут искаться файл с расширением `.tpl`
    """

    context: dict[str, str] = {}
    cli_args: TArgs = parse_args(
        argv[0],
        argv[1:],
    )
    ##
    # Ели не переданы ни каких данных то выводим документацию по CLI
    ##
    if len(argv) == 1:
        log(main.__doc__)
    ###
    # Получаем данные для шаблона
    ##
    if path_to_context := cli_args.named_args.get('c'):
        path_to_context = path_to_context[0]
        context = json.loads(pathlib.Path(path_to_context).read_text())
    ##
    # Собираем шаблоны для указанных файлов
    ##
    if path_to_templates := cli_args.named_args.get('f'):
        # Перебираем файлы
        for _files in path_to_templates:
            template_str: str = pathlib.Path(_files).resolve().read_text()
            build_text: str = build_conf(template_str, context)
            save_tpl_file(_files, build_text)
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
