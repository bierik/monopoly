#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Development")
    try:
        from configurations.management import execute_from_command_line
    except ImportError as exc:
        err = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        raise ImportError(err) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
