import filecmp
import os
import re
import json
import pathlib
import shutil
from jinja2 import Template
from .pypars import files_from_path, parse_args, TArgs
from .helper import color, jsonc_to_json, log


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
{y}-c{r} context.jsonc             = {d}[!]{r} Указать путь к файлу({u}context.jsonc{r}), из которого будут браться данными для шаблонов.
{f}> Шаблонные файлы{r}
{y}-f{r} Файл0 Файл1              = {g}[?]{r} Указать конкретные файлы, с расширением {u}.tpl{r}.
{y}-d{r} Директория0 Директория1  = {g}[?]{r} Указать путь к директории, в которой будут искаться все файлы с расширением {u}.tpl{r}.
{f}> Шаблонный проект{r}
{y}-ti{r} Директория              = {g}[?]{r} Указать путь к папке с шаблоном проекта.
{y}-to{r} Директория              = {g}[?]{r} Указать путь куда собрать шаблонный проект.

{c}Flags{r}:
{y}-e_{r}                         = {g}[?]{r} Если указа этот флаг то также создастся {u}.env{r} файл, в те же папки где файл {u}context.jsonc{r}.
{y}-y_{r}                         = {g}[?]{r} Ответить на все вопросы {u}yes{r}.
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    """

    context: dict[str, str] = {}
    cli_args: TArgs = parse_args(
        argv[0],
        argv[1:],
    )
    # Путь к файлу `context.jsonc`
    path_to_context: pathlib.Path
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
    context: dict | list = {}
    if path_to_context := cli_args.named_args.get('c'):
        path_to_context = pathlib.Path(path_to_context[0])
        context = jsonc_to_json(path_to_context.read_text())
    else:
        print("WARNING:\tНе указан путь к `context.jsonc`")
    ##
    # Собираем шаблоны для указанных файлов
    ##

    def _build_tpl(_files: str):
        # Шаблонный файл должке оканчиваться на `.tpl`
        if re.search('\.tpl\Z', str(_files)):
            # Получаем текст шаблона
            template_str: str = pathlib.Path(_files).resolve().read_text()
            # Собираем текст на основе контекста
            build_text: str = build_conf(template_str, context)
            # Сохраняем собранный текст в файл
            save_tpl_file(_files, build_text)
            # Добавить папку в используемые
            use_paths_dirs.add(pathlib.Path(_files).parent.resolve())

    if path_to_templates := cli_args.named_args.get('f'):
        # Перебираем файлы
        for _files in path_to_templates:
            _build_tpl(_files)
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
            # Записываем в файл `.env` в туже папку где `context.jsonc`
            (path_to_context.parent / '.env').write_text(
                '\n'.join(write_text)
            )
    ###
    # Работа с шаблонным проектом
    ###

    def _skip(_file):
        log('{c}Skip{r}:\t{f}'.format(
            c=color.сyan.value, r=color.reset.value, f=_file
        ))
    if path_in_template := cli_args.named_args.get('ti'):
        path_in_template = pathlib.Path(path_in_template[0]).resolve()
        # Если есть `-ti` то должен быть и `-to`
        if path_out_template := cli_args.named_args.get('to'):
            path_out_template = pathlib.Path(path_out_template[0]).resolve()
            # Перебираем файлы в шаблонном проекте.
            for _files in files_from_path(path_in_template):
                # Полное имя файла, для нового проекта.
                write_name_file = pathlib.Path(_files.replace(
                    str(path_in_template), str(path_out_template)
                ))
                # Создаем путь из папок, для нового проекта.
                os.makedirs(write_name_file.parent, exist_ok=True)
                # Если не перед флаг `-y_`, то проверяем содержания файлов в шаблоне, и в новом проекте.
                if 'y' not in cli_args.flags:
                    # 1: Если файл уже существует
                    if write_name_file.exists():
                        # 2: и его содержание отличается от шаблона
                        if not filecmp.cmp(_files, write_name_file):
                            # 3: то запрашиваем подтверждение на перезапись файла
                            res_is_replace = input(
                                f"{color.read.value}Файл уже существует и отличается от шаблона, перезаписать его ?{color.reset.value}: {write_name_file}\n[y|N]>>>"
                            )
                            # Если ответ не положительный то пропускам файл
                            if res_is_replace != 'y':
                                _skip(write_name_file)
                                continue
                        # Если файл уже существует, и его содержание равно шаблону, то пропускаем его
                        else:
                            _skip(write_name_file)
                            continue
                # Копируем файл из шаблона в новый проект.
                shutil.copy(_files, write_name_file.parent)
                log("{y}Copy{r}:\t{f}".format(
                    y=color.yellow.value, r=color.reset.value, f=write_name_file
                ))
                # Собираем файл уже в новом проекте.
                _build_tpl(write_name_file)
        else:
            raise KeyError('Не передан ключ -to')
