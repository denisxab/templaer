# Запустить ASGI сервер
run:
	daphne conf.asgi:application -b 0.0.0.0 -p 8000

# Собрать проект, собрать статические файлы, создать миграции в БД
build:
	python manage.py collectstatic ; python manage.py makemigrations && python manage.py migrate ; python manage.py makemigrations api && python manage.py migrate api

# Экспортировать зависимости Python в файл `requirements.txt`, например, для того чтобы установить их в контейнере через обычный `pip` 
poetry_export:
	poetry export --dev --format requirements.txt --output requirements.txt
