import enum
import json
import re


class color(enum.Enum):
    reset = '\x1b[0m'
    #################
    green = '\x1b[92m'
    yellow = '\x1b[93m'
    read = '\x1b[31m'
    сyan = '\x1b[36m'
    fil = '\033[35m'
    # Рамка
    frame = '\x1b[51m'


def log(text: str):
    print(text)


def jsonc_to_json(jsonc_text: str) -> object:
    """
    Json c комментариями это Jsonc
    """
    # Убираем комментарии из Jsonc
    json_text = re.sub(
        '(?P<one_line>[\t ]+\/+[^\n]{2,})|(?P<mlt_line>\/\*(?:.?\s*(?!\*?\/))*[\w\W]?\*\/)', '', jsonc_text
    )
    return json.loads(json_text)
