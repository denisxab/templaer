# import asyncio
import os
import pprint
import re
import subprocess

# from asyncio import create_subprocess_shell
from pathlib import Path
from typing import Any

from django.db import connection
from django.db.backends.utils import CursorWrapper

"""
setting.py
"""


def read_env_file_and_set_from_venv(file_name: str):
    """Чтение переменных окружения из указанного файла, и добавление их в ПО `python`"""
    # os.environ = {}
    with open(file_name, "r", encoding="utf-8") as _file:
        res = {}
        for line in _file:
            tmp = re.sub(r"^#[\s\w\d\W\t]*|[\t\s]", "", line)
            if tmp:
                k, v = tmp.split("=", 1)
                # Если значение заключено в двойные кавычки, то нужно эти кавычки убрать
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                res[k] = v
    os.environ.update(res)
    pprint.pprint(os.environ._data)


def _subprocess_run(command: str) -> str:
    """Выполнить Bash команду и вернуть ответ в return"""
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout.decode().strip().replace('"', "")


# async def _subprocess_run_async(command: str) -> str:
#     """Выполнить Bash команду и вернуть ответ в return"""
#     res = await create_subprocess_shell(
#         cmd=command,  # Текст команды
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE, shell=True
#     )
#     # Получить результат выполнения команды
#     stdout, stderr = await res.communicate()
#     return stdout.decode().strip()


def files_from_path(path: str | Path, regex: str | None = None) -> Path:
    """
    Получить всей файлы в указанной директории с учетом вложенности

    path: Путь к папке
    """

    # Проходим рекурсивно по всем поддиректориям и файлам внутри них
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            # Проверяем на соответствие указному шаблону, если нет то пропускам путь.
            if regex and not re.search(regex, filename):
                continue
            # Получаем полный путь к файлу.
            yield Path(os.path.join(dirpath, filename))


def default_host_postgresql_from_docker_compose() -> str:
    """
    По умолчанию получаем IP контейнера из DockerCompose
    """
    ###
    # Ищем имя папки где храниться `docker-compose.yml`
    path_where_docker_compose: Path = list(files_from_path(Path(__file__).parent.parent, "docker-compose.yml"))[0]
    dir_where_docker_compose: str = path_where_docker_compose.parent.stem
    ##
    command = f"""
    # Получить имя контейнера с PostgreSql в docker-compose
    nc=`docker ps | grep -Po '[\w\d]+_postgres_[\w\d]+'`;
    # Имя папки где храниться `docker-compose.yml`
    p="{dir_where_docker_compose}";
    # Получить имя сети
    nn=`docker network ls | grep -Po "$p"+"[\w\d]+"`;
    # Получить IP контейнера из DockerCompose
    docker inspect $nc | jq ".[0].NetworkSettings.Networks.$nn.IPAddress"
    """
    # return asyncio.run(_subprocess_run_async(command)).replace('"', '')
    return _subprocess_run(command).replace('"', "")


"""
SQL
"""


def get_db_cursor(fun):
    """
    Вернуть курсор для выполнения Raw SQL команд

    Пример использования:

    ```
    from rest_framework.views import APIView


    class ИмяКласса(APIView):
        @get_db_cursor
        def get(self, request: Request, cursor: CursorWrapper):
            cursor.execute('SQL_Запрос')
            res = cursor.fetchall()
            print(res)
    ```
    """

    def wrapper(*arg, **kwargs):
        with connection.cursor() as cursor:
            cursor: CursorWrapper
            kwargs["cursor"] = cursor
            res = fun(*arg, **kwargs)
        return res

    return wrapper


def dictfetchall(cursor: CursorWrapper) -> list[dict[str, Any]]:
    "Вернуть результат в виде dist"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
