import os
import re
import json
import pathlib
import shutil
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
    in_file = str(in_file)
    # Обрезать `.tpl` с конца имени файла
    path_save = re.sub('\.tpl\Z', '', in_file)
    if in_file != path_save:
        # Сохранить текст в новый файл
        pathlib.Path(path_save).write_text(write_text)
        log(f'{color.green.value}Build:{color.reset.value}\t{path_save}')


def main(argv: list[str]):
    """
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
{y}Templaer{r} - универсальный CLI шаблонизатор конфигурационных файлов, основанный на {u}Jinja2{r}.

{g}* GitHub{r} = https://github.com/denisxab/templaer
{g}* Pip{r}    = https://pypi.org/project/templaer/
{g}* Habr{r}   = https://habr.com/ru/post/717996/
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
{c}Описание CLI{r}: 
{d}[!]{r} - Обязательный для передачи
{g}[?]{r} - Опциональный для передачи

{c}Kwargs{r}:
{y}-c{r} context.json             = {d}[!]{r} Указать путь к файлу({u}context.json{r}), из которого будут браться данными для шаблонов.
{f}> Шаблонные файлы{r}
{y}-f{r} Файл0 Файл1              = {g}[?]{r} Указать конкретные файлы, с расширением {u}.tpl{r}.
{y}-d{r} Директория0 Директория1  = {g}[?]{r} Указать путь к директории, в которой будут искаться все файлы с расширением {u}.tpl{r}.
{f}> Шаблонный проект{r}
{y}-ti{r} Директория              = {g}[?]{r} Указать путь к папке с шаблоном проекта.
{y}-to{r} Директория              = {g}[?]{r} Указать путь куда собрать шаблонный проект.

{c}Flags{r}:
{y}-e_{r}                         = {g}[?]{r} Если указа этот флаг то также создастся {u}.env{r} файл, в те же папки где файл {u}context.json{r}
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
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
        log(main.__doc__.format(
            r=color.reset.value,
            g=color.green.value,
            y=color.yellow.value,
            c=color.сyan.value,
            d=color.read.value,
            f=color.fil.value, u='\033[1m'
        )[1:])
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

    def a1(_files: str):
        template_str: str = pathlib.Path(_files).resolve().read_text()
        build_text: str = build_conf(template_str, context)
        save_tpl_file(_files, build_text)
        # Добавить папку в используемые
        use_paths_dirs.add(pathlib.Path(_files).parent.resolve())
    ##
    # Собираем шаблоны для указанных файлов
    ##
    if path_to_templates := cli_args.named_args.get('f'):
        # Перебираем файлы
        for _files in path_to_templates:
            a1(_files)
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
    ###
    # Работа с шаблонным проектом
    ###
    if path_in_template := cli_args.named_args.get('ti'):
        path_in_template = pathlib.Path(path_in_template[0]).resolve()
        # Если есть `-ti` то должен быть и `-to`
        if path_out_template := cli_args.named_args.get('to'):
            path_out_template = pathlib.Path(path_out_template[0]).resolve()
            # Перебираем файл в шаблонном проекте.
            for _files in files_from_path(path_in_template):
                # Создаем полное имя файла, для нового проекта.
                write_name_file = pathlib.Path(_files.replace(
                    str(path_in_template), str(path_out_template)
                ))
                # Создаем путь из папок, для нового проекта.
                os.makedirs(write_name_file.parent, exist_ok=True)
                # Копируем файл из шаблона в новый проект.
                shutil.copy(_files, write_name_file.parent)
                # Собираем файл уже в новом проекте.
                a1(write_name_file)
        else:
            raise KeyError('Не передан ключ -to')
