import os
from pathlib import Path


def abPath(relDir):
    return str(Path( relDir).resolve().absolute())

def getPath(dir, date, file):
    return os.path.join(abPath(dir), date, file)

