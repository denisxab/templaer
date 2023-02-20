# Templaer

Templaer - универсальный CLI шаблонизатор конфигурационных файлов, основанный на `Jinja2`.

## Установка

1. Установить `templaer`

    ```bash
    pip install templaer
    ```

2. Получить подсказку по CLI

    ```bash
    python -m templaer
    ```

## Примеры CLI

- Поиск в указанной директории всех файлов с которые оканчиваются на `.tpl`, и сборка этих файлов.

    ```bash
    python -m templaer -c context.json -d Папка  
    ```

- Собрать указанные файлы.

    ```bash
    python -m templaer -c context.json -f Файл1.conf.tpl Файл2.tpl
    ```

## Основы шаблонов на Jinja2

### Тернарный условный оператор

В этом примере показано как в зависимости от переменной `DEBUG`, будет поставлено значение из переменной `PORT_D` или `PORT_R`.

1. Содержание файла `context.json`:

    ```json
    {
        "DEBUG": false,
        "PORT_D": 8080,
        "PORT_R": 80
    }
    ```

2. Содержание файла `ЛюбойФайл.conf.tpl`:

    ```nginx
    server {
        listen {{ PORT_D if DEBUG else PORT_R }};
        server_name "localhost";

        location / {
            default_type text/html;
            return 200 'ok';
        }
    }
    ```

3. Соберем файл используя команду:

    ```bash
    python -m templaer -c context.json -f ЛюбойФайл.conf.tpl
    ```

4. В итоге создастся(или перезапишитесь) новый файл `ЛюбойФайл.conf`, с содержанием:

    ```nginx
    server {
        listen 80;
        server_name "localhost";

        location / {
            default_type text/html;
            return 200 'ok';
        }
    }
    ```
