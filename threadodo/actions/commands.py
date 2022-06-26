import sys
import typing
from typing import Optional, Union, Tuple, List, Dict
from threadodo.actions.action import Action
from threadodo.logger import init_logger

from tweepy import Response
import parse

class Command(Action):
    """
    An action invoked by tweeting at the bot and telling it to do something
    """
    name:str
    arguments:Optional[List[str]] = None
    parse_str = "@{username}:{command}"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.logger = init_logger('threadodo.action.command.'+self.name, self.bot.basedir)



    def check(self, response:Response) -> bool:
        """
        Check if the response has a first line like::

            @{bot.username}: {Command.name}


        Args:
            response:

        Returns:
            bool
        """
        # like
        # "{@

        # split into lines
        lines = str(response.data.text).split('\n')
        test_str = lines[0].strip()
        self.logger.debug(f"Testing string: {test_str}")

        parse_res = parse.parse(self.parse_str, test_str)
        self.logger.debug(f"parse result: {parse_res}")
        if parse_res is None:
            self.logger.debug('parse match was None')
            return False

        parse_dict = {
            'username': parse_res.named['username'].strip(),
            'command': parse_res.named['command'].strip(),
        }
        if parse_dict['username'] == self.bot.username and \
                parse_dict['command'] == self.name:
            return True
        else:
            return False

class Identify(Command):
    name="identify"


