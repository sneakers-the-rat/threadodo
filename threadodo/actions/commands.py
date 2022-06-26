import sys
import typing
from typing import Optional, Union, Tuple, List, Dict
from threadodo.actions.action import Action

class Command(Action):
    """
    An action invoked by tweeting at the bot and telling it to do something
    """
    name:str
    arguments:Optional[List[str]] = None
