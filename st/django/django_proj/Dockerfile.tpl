# Начинаем с базового образа python 3.8
FROM python:3.11-alpine

# Объявляем рабочую директорию
WORKDIR /code
# Копируем Django проект
COPY . /code/
# Установка зависемостей для Python
RUN pip install --upgrade pip && pip install -r requirements.txt
# Войти в диреткорию с проектом
#### 
ENV PORT_WEB={{DJANGO_PORT}}
# Используемый порт
EXPOSE $PORT_WEB
# Запускаем приложение
CMD {{ 'python manage.py runserver 0.0.0.0:${PORT_WEB}' if DEBUG else  'daphne conf.asgi:application -b 0.0.0.0 -p ${PORT_WEB}' }}
