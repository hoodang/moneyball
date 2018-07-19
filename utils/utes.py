import os
from pathlib import Path


def abPath(relDir):
    return str(Path( relDir).resolve().absolute())

def getPath(dir, date, file):
    return os.path.join(abPath(dir), date, file)

def load_properties(filepath, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    with open(filepath, "r") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"').replace(r'\\', '')
                props[key] = value
                os.environ[key] = value
    return props