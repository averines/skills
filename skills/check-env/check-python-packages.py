#!/usr/bin/env python3
"""Inspect distribution metadata in this interpreter; never import the packages."""
import os
import re
import shlex
import sys


def main():
    if sys.version_info < (3, 8):
        print('[UNKNOWN] Python package checks require Python 3.8+')
        return 2
    from importlib.metadata import PackageNotFoundError, version

    packages = sys.argv[1:] or ['requests', 'Pillow', 'pandas', 'openpyxl', 'python-docx', 'pypdf']
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', name) for name in packages):
        print('[UNKNOWN] Invalid distribution name')
        return 2
    print('Python interpreter: ' + sys.executable)
    missing = []
    for name in packages:
        try:
            installed = version(name)
        except PackageNotFoundError:
            print('[MISSING] ' + name)
            missing.append(name)
        except Exception as exc:
            print('[UNKNOWN] ' + name + ': metadata probe failed (' + type(exc).__name__ + ')')
        else:
            print('[OK] ' + name + ' ' + installed)
    if missing:
        print('\nSuggestions only: prefer the project environment and dependency files.')
        if sys.prefix != sys.base_prefix:
            executable = sys.executable
        else:
            print('If the project has no environment, create one with this Python:')
            if os.name == 'nt':
                print("  & '" + sys.executable.replace("'", "''") + "' -m venv .venv")
                executable = '.venv/Scripts/python.exe'
            else:
                print('  ' + shlex.quote(sys.executable) + ' -m venv .venv')
                executable = '.venv/bin/python'
        if os.name == 'nt':
            command = "& '" + executable.replace("'", "''") + "'"
        else:
            command = shlex.quote(executable)
        print('  ' + command + ' -m pip install ' + ' '.join(missing))
    return 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if not stream.isatty() and hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(main())
