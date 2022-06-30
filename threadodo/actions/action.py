import sys
from abc import ABC, abstractmethod
import typing
from typing import Optional, Union, Tuple, List, Dict
from dataclasses import dataclass

from tweepy import Response

if typing.TYPE_CHECKING:
    from threadodo.bot import Threadodo


@dataclass
class Result:
    ok:bool
    """
    Whether the action completed successfully
    """
    log: Optional[str] = None
    """
    Message to log
    """
    reply: Optional[str] = None
    """
    Message to reply with
    """



class Action(ABC):

    def __init__(self, bot:'Threadodo'):
        super(Action, self).__init__()
        self.bot = bot

    #@abstractmethod
    def do(self, response:Response) -> Result:
        """
        Encapsulate the other actions and uh do the action!
        Returns:
            :
        """

    #@abstractmethod
    def check(self, response:Response) -> bool:
        """
        Check if the condition of this action is met
        """


    #@abstractmethod
    def get(self, response:Response) -> typing.Any:
        """
        If this action sets something, get its value.

        Eg. if this action sets a

        Returns:

        """

