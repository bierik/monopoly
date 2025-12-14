import os
import sys


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
if sys.platform == "darwin":
    os.environ.setdefault("DJANGO_CONFIGURATION", "Testing")


def main():
    from configurations.management import execute_from_command_line  # noqa: PLC0415

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
