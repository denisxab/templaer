#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from helper_dj import default_host_postgresql_from_docker_compose


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
    # По умолчанию получаем IP контейнера с PostgreSQL из DockerCompose
    os.environ.setdefault("POSTGRES_HOST_DEFAULT", default_host_postgresql_from_docker_compose())

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
