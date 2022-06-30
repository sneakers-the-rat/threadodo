from pathlib import Path
import logging
import tweepy
import typing
import pdb
from typing import List, Optional, Type

from threadodo.creds import Creds, Zenodo_Creds
from threadodo.thread import Thread
from threadodo.zenodo import post_pdf, Deposition
from threadodo.logger import init_logger
from threadodo.actions import checks, commands
if typing.TYPE_CHECKING:
    from threadodo.actions import Action


class Threadodo(tweepy.StreamingClient):
    check_classes = [checks.Mentioned] # type: List[Type[checks.Check]]
    command_classes = [commands.Identify] # type: List[Type[commands.Command]]

    def __init__(
            self,
            creds:Path = Path('twitter_creds.json'),
            zenodo_creds:Path = Path('zenodo_creds.json'),
            username:str='threadodo_bot',
            basedir:Path=Path().home()/"threadodo",
            loglevel="DEBUG",
            debug:bool = False
    ):

        self._creds = None
        self._zenodo_creds = None
        self._client = None
        self.basedir=Path(basedir)

        self.creds_path = Path(creds)
        self.zenodo_creds_path = Path(zenodo_creds)
        self.username = username
        self.debug = debug
        self.logger = init_logger('threadodo.bot', basedir, loglevel=loglevel)

        super(Threadodo, self).__init__(self.creds.bearer_token)

        self.add_rules(tweepy.StreamRule(f'@{self.username}'))

        self.checks = [cls(self) for cls in self.check_classes]
        self.commands = [cls(self) for cls in self.command_classes]


    def on_response(self, response:tweepy.Response):
        """
        Convert thread to pdf, then like yno archive it on zenodo
        """

        if self.debug:
            pdb.set_trace()

        self.logger.info(f'Mentioned: {response.data.text}')


        # Do checks to see if we should do anything!
        for check in self.checks:
            res = check.do(response)
            if not res.ok:
                if res.log:
                    self.logger.info(res.log)
                return

        # Determine what action we should do!
        for command in self.commands:
            if command.check(response):
                self.logger.info(f"Given Command {command.name}")
                res = command.do(response)
                if res.log:
                    self.logger.debug(res.log)
                if res.reply:
                    self.reply(response, res.reply)
                return

        # TODO: move this to a command class
        # thread = Thread.from_tweet(self.creds, response)
        # self.logger.info('thread received')
        # try:
        #     pdf = thread.to_pdf()
        #     self.logger.info('pdf created')
        #     depo = post_pdf(pdf, thread, self.zenodo_creds)
        #     self.logger.info('posted pdf')
        #     self.logger.debug(depo)
        #
        # finally:
        #     pdf.unlink()
        #
        # self.reply_completed(response, depo)


    def reply_completed(self, response: tweepy.Response, deposit:Deposition):

        self.client.create_tweet(text=f"The preprint of your thread is ready: {deposit.doi_url} - {deposit.title}",
                            in_reply_to_tweet_id=response.data.id)
        self.logger.info('replied')

    def reply(self, response: tweepy.Response, text:str):
        self.client.create_tweet(text=text,
                                 in_reply_to_tweet_id=response.data.id)



    def run(self, threaded:bool=False):
        self.logger.debug('starting')
        self.filter(threaded=threaded,
                    tweet_fields=[
                        "in_reply_to_user_id",
                        "author_id",
                        "created_at",
                        "conversation_id",
                        "entities",
                        "referenced_tweets"
                    ],
                    expansions=[
                        'author_id'
                    ]
                    )
        self.logger.debug('stopped')

    @property
    def client(self) -> tweepy.Client:
        if self._client is None:
            self._client = tweepy.Client(
                consumer_key=self.creds.api_key,
                consumer_secret=self.creds.api_secret,
                access_token=self.creds.access_token,
                access_token_secret=self.creds.access_secret)
        return self._client

    @property
    def creds(self) -> Creds:
        if self._creds is None:
            self._creds = Creds.from_json(self.creds_path)
        return self._creds

    @property
    def zenodo_creds(self) -> Zenodo_Creds:
        if self._zenodo_creds is None:
            self._zenodo_creds = Zenodo_Creds.from_json(self.zenodo_creds_path)
        return self._zenodo_creds



