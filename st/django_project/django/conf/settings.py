"""
Django settings for conf project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
import pprint
import re

###
# Путь к Django проекту
BASE_DIR = Path(__file__).resolve().parent.parent
# Путь к корню проекта
ROOT_DIR = BASE_DIR.parent


def read_env_file_and_set_from_venv(file_name: str):
    """Чтение переменных окружения из указанного файла, и добавление их в ПО `python`"""
    with open(file_name, 'r', encoding='utf-8') as _file:
        res = {}
        for line in _file:
            tmp = re.sub(r'^#[\s\w\d\W\t]*|[\t\s]', '', line)
            if tmp:
                k, v = tmp.split('=', 1)
                # Если значение заключено в двойные кавычки, то нужно эти кавычки убрать
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                res[k] = v
    os.environ.update(res)
    pprint.pprint(res)


read_env_file_and_set_from_venv(BASE_DIR / ".env")

###
# Секретный ключ приложения
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
# Если `True` будет отображать отладочную информацию
DEBUG = os.environ.get('DEBUG', True)
# Список хостов который будет обслуживать Django
ALLOWED_HOSTS = ['*']
# Главный `URL` обработчик
ROOT_URLCONF = 'conf.urls'
# Обработка ASGI
ASGI_APPLICATION = 'conf.asgi.application'
# Обработка WSGI
WSGI_APPLICATION = 'conf.wsgi.application'

###
# Все инсталлированные приложения на вашем сайте.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "api"
]
# Список используемых плагинов.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

###
# Список, содержащий настройки для всех шаблонизаторов,
# которые будут использоваться с Джанго. Каждый элемент списка
# представляет собой словарь, содержащий параметры для индивидуального двигатель
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

###
# Database
# Словарь, содержащий настройки для всех баз данных,
# которые будут использоваться с Джанго.
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        # Адаптер
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Имя Бд
        'NAME': os.environ['POSTGRES_DB'],
        # Имя пользователя
        'USER': os.environ['POSTGRES_USER'],
        # Пароль от пользователя
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        # Хост, имя контейнера.
        'HOST': os.environ.get('POSTGRES_HOST', default='localhost'),
        # Порт для подключения к БД.
        'PORT': os.environ.get('POSTGRES_PORT', default=5432),
    }
}
# Автоматически добавлять поле primary_key к БД
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

###
# Кеширование данных в файловой системе
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, '__cache')
    }
}

###
# Password validation
# Список валидаторов,
# которые используются для проверки надежности паролей пользователей.
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

###
# Internationalization
# Локализация
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LANGUAGE_CODE = 'ru'  # Язык сервера
# Логическое значение, указывающее, должна ли быть включена система перевода Django.
USE_I18N = True
TIME_ZONE = 'Europe/Moscow'  # Часовой пояс
USE_L10N = True  # Логическое значение, указывающее, будет ли включено локализованное форматирование данны
USE_TZ = True  # Логическое значение, указывающее, будут ли даты по умолчанию учитывать часовой пояс

###
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
# URL-адрес для использования при обращении к статическим файлам, расположенным в STATIC_ROOT.
STATIC_URL = '/static/'
# Путь к общей статической папки.
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [  # Список нестандартных путей используемых для сборки.
    # os.path.join(BASE_DIR, "static"),
]
# Пути для изображений
# Имя папки в корневом каталоге, для изображений
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'  # Добавляет к файлам префикс
#####


# Для отладки
if DEBUG:
    ###
    # django-debug-toolbar
    # INSTALLED_APPS.append('debug_toolbar')
    # INTERNAL_IPS = ['127.0.0.1']
    # MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

    # django-livereload-server
    # INSTALLED_APPS.append('livereload')
    # MIDDLEWARE.append('livereload.middleware.LiveReloadScript')

    ###
    # Отключить кеширование при отладке
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }