import logging
from rich.logging import RichHandler
from pathlib import Path
import sys
import typing
from typing import Optional, Union, Tuple, List, Dict, Literal
from logging.handlers import RotatingFileHandler

def init_logger(
        name:Optional[str]=None,
        basedir:Optional[Path]=None,
        loglevel:str='DEBUG',
        loglevel_disk:Optional[str]=None
        ):
    if name is None:
        name = 'threadodo'
    else:
        if not name.startswith('threadodo'):
            name = '.'.join(['threadodo', name])

    if loglevel_disk is None:
        loglevel_disk = loglevel

    logger = logging.getLogger(name)
    logger.setLevel(loglevel)


    if basedir is not None:
        logger.addHandler(_file_handler(basedir, name, loglevel_disk))

    logger.addHandler(_rich_handler())
    return logger


def _file_handler(basedir:Path, name:str, loglevel:str="DEBUG") -> RotatingFileHandler:
    filename = Path(basedir) / '.'.join([name, 'log'])
    basedir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        str(filename),
        mode='a',
        maxBytes=2 ** 24,
        backupCount=5
    )
    file_formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]: %(message)s")
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(file_formatter)
    return file_handler

def _rich_handler() -> RichHandler:
    rich_handler = RichHandler(rich_tracebacks=True, markup=True)
    rich_formatter = logging.Formatter(
        "[bold green]\[%(name)s][/bold green] %(message)s",
        datefmt='[%y-%m-%dT%H:%M:%S]'
    )
    rich_handler.setFormatter(rich_formatter)
    return rich_handler