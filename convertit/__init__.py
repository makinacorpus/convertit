import os
import subprocess

PROGRAMS = {}


def which(program):
    """Cached call to which"""
    if program not in PROGRAMS:
        PROGRAMS[program] = subprocess.check_output(['which', program]).strip()
    return PROGRAMS[program]


def exists(program=None):
    try:
        which(program)  # raise on failure
        result = True
    except Exception:
        result = False
    return result


def create_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
