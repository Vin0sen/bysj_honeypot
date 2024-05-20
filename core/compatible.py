#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import concurrent
import sys
import os
import random
import string
import shutil
import inspect
from core.color import reset_cmd_color
# from core.exit_helper import exit_failure
from datetime import datetime


def now(model="%Y-%m-%d %H:%M:%S"):
    """
    get now date and time
    Args:
        model:  the date and time model, default is "%Y-%m-%d %H:%M:%S"
    Return the date and time of now
    """
    return datetime.now().strftime(model)


def hours(hour_to_seconds):
    """
    integer to hour(s)
    Args:
        hour_to_seconds: hours (integer)
    Return seconds equal to hours (integer)
    """

    return int(hour_to_seconds * 60 * 60)

def logo():
    from core.alert import write_to_api_console
    write_to_api_console(open('.logo').read())
    reset_cmd_color()


def version():
    """
    version of python

    Returns:
        integer version of python (2 or 3)
    """
    return int(sys.version_info[0])


def os_name():
    """
    OS name

    Returns:
        OS name in string
    """
    return sys.platform


def get_timeout_error():
    """
    Get the timeout error thrown by pyshark apply_on_packets function
    """
    try:
        # If asyncio timeout error exists, this will be returned
        return asyncio.exceptions.TimeoutError
    except Exception:
        # For older python versions, where asyncio timeout error
        # doesn't exist, this one will be returned.
        return concurrent.futures._base.TimeoutError


def make_tmp_thread_dir():
    """
    create random thread directory
    example: tmp/thread_saGK78HhJ3fk6BN
    Returns:
        name of directory or False
    """
    uppercase_string = string.ascii_uppercase
    lowercase_string = string.ascii_lowercase
    digits = string.digits
    combined_string = uppercase_string + lowercase_string + digits
    return mkdir(
        "tmp/thread_" + "".join(
            [
                combined_string[random.randint(0, len(combined_string) - 1)] for _ in range(15)
            ]
        )
    )


def mkdir(dir):
    """
    create directory

    Args:
        dir: directory path

    Returns:
        Name of directory or False
    """
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except Exception:
            return False
    return dir


def copy_dir_tree(src, dst, symlinks=True, ignore=None):
    """
    copytree a directory

    Args:
        src: source directory
        dst: destination directory
        symlinks: copy symlinks
        ignore: ignore

    Returns:
        True
    """
    # https://stackoverflow.com/a/12514470
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
    return True


def get_module_dir_path(module):
    """
    get a module path

    Args:
        module: module

    Returns:
        path
    """
    return os.path.dirname(
        inspect.getfile(module)
    )


def generate_token(length=32):
    """
    generate token using hex chars

    Args:
        length: length of token - default 32

    Returns:
        token string
    """
    return "".join(random.choice("0123456789abcdef") for _ in range(length))


def byte_to_str(data):
    """
    convert data to str

    :param data: data
    :return: str(data)
    """
    return str(
        data if isinstance(data, str) else data.decode() if data is not None else ""
    )


def is_verbose_mode():
    """
    is run as verbose mode?

    :return: boolean
    """
    return '--verbose' in sys.argv or '-v' in sys.argv
