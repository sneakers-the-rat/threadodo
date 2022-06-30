import pdb
import sys
import typing
from typing import Optional, Union, Tuple, List, Dict
from threadodo.actions.action import Action, Result
from threadodo.logger import init_logger
from dataclasses import dataclass
import re

from tweepy import Response, StreamResponse
import parse

@dataclass
class Command_Params:
    username: str
    command: str
    args: Optional[dict]

class Command(Action):
    """
    An action invoked by tweeting at the bot and telling it to do something
    """
    name:str
    command_str = r"@(?P<username>\S{1,})\s*(?P<command>\w*)"
    arg_str = r"^(\w*?):\s*(.*)"

    @dataclass
    class Arguments:
        pass


    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.logger = init_logger('threadodo.action.command.'+self.name, self.bot.basedir)
        self.command_pattern = re.compile(self.command_str)
        self.arg_pattern = re.compile(self.arg_str, re.MULTILINE)


    @classmethod
    def parse(cls, tweet:Union[str, Response]) -> Union[None, Command_Params]:
        if isinstance(tweet, (Response, StreamResponse)):
            tweet = tweet.data.text
        command_pattern = re.compile(cls.command_str)
        arg_pattern = re.compile(cls.arg_str, re.MULTILINE)

        command_tup = command_pattern.findall(tweet)
        command_tup = [c for c in command_tup if len(c) == 2 and len(c[0])>0 and len(c[1])>0]

        if len(command_tup) == 0:
            return None

        else:
            param_dict = {'username': command_tup[0][0], 'command': command_tup[0][1]}

        args = arg_pattern.findall(tweet)
        if args is not None:
            param_dict['args'] = dict(args)

        return Command_Params(**param_dict)



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

        command_tup = self.command_pattern.findall(test_str)
        command_tup = [c for c in command_tup if len(c) == 2 and len(c[0]) > 0 and len(c[1]) > 0]

        if len(command_tup) == 0:
            parse_res = None

        else:
            parse_res = {'username': command_tup[0][0], 'command': command_tup[0][1]}

        self.logger.debug(f"parse result: {parse_res}")
        if parse_res is None:
            self.logger.debug('parse match was None')
            return False

        if parse_res['username'] == self.bot.username and \
                parse_res['command'] == self.name:
            return True
        else:
            return False

    def get(self, response:Response) -> Union[Command_Params, None]:
        """Get the value of a command

        Response must have the 'user_id' expansion
        """
        matched = self.bot.client.search_recent_tweets(
            f"from:{response.includes['users'][0]['username']} @{self.bot.username} \"{self.name}\"",
        user_auth=True)
        self.logger.debug("matched get request")
        self.logger.debug(matched)
        if matched.data is None:
            return None

        all_params = [self.parse(d.text) for d in matched.data]
        found_params = [p for p in all_params if len(p.args)>0]
        if len(found_params)>0:
            return found_params[0]
        else:
            return all_params[0]





    def arg_dict(self, tweet:Union[str, Response]) -> dict:
        """
        Get arguments given to this command
        """
        if isinstance(tweet, Response):
            tweet = tweet.data.text

        return dict(self.arg_pattern.findall(tweet))

    @classmethod
    def example(cls) -> str:
        ex_str = f"@<bot> {cls.name}"
        keys = [f"{key}:" for key in cls.Arguments.__dataclass_fields__.keys()]
        ex_str = "\n".join([ex_str, *keys])
        return ex_str


class Identify(Command):
    name="identify"

    @dataclass
    class Arguments:
        name: str
        affiliation: Optional[str]
        orcid: Optional[str]

    def do(self, response:Response) -> Result:
        params = self.parse(response)
        if len(params.args) == 0:
            id = self.get(response)

            if id is None or len(id.args)==0:
                reply = "No Identity Found! Set one by tweeting:\n"+self.example()
                log = "Help message given"
            else:
                reply = "Previous Identity Found: \n" + "\n".join([f"{key}: {val}" for key, val in id.args.items()])
                log = "previous identity given"
        else:
            reply = "Identity registered! This will be used to identify all threads from your username. If you need to update or remove your identity, delete this tweet, your information is not stored anywhere else."
            log = f"Identity registered"
        return Result(ok=True, reply=reply, log=log)




