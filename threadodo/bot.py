from pathlib import Path
from pprint import pprint
import logging
import pdb

import tweepy

from threadodo.creds import Creds, Zenodo_Creds
from threadodo.thread import Thread
from threadodo.zenodo import post_pdf, Deposition


class Threadodo(tweepy.StreamingClient):

    def __init__(
            self,
            creds:Path = Path('twitter_creds.json'),
            zenodo_creds:Path = Path('zenodo_creds.json'),
            username:str='threadodo_bot',
            loglevel="DEBUG"
    ):

        self._creds = None
        self._zenodo_creds = None
        self.creds_path = Path(creds)
        self.zenodo_creds_path = Path(zenodo_creds)
        self.username = username

        super(Threadodo, self).__init__(self.creds.bearer_token)

        self.add_rules(tweepy.StreamRule(f'@{self.username}'))
        self.logger = logging.Logger('threadodo.bot')
        self.logger.setLevel(loglevel)


    def on_response(self, response:tweepy.Response):
        """
        Convert thread to
        :param response:
        :return:
        """
        pdb.set_trace()
        pprint(response)
        if not self._check_mentioned(response.data):
            self.logger.info('Stream received, but was not directly mentioned')
            return

        thread = Thread.from_tweet(self.creds, response)
        self.logger.info('thread received')
        try:
            pdf = thread.to_pdf()
            self.logger.info('pdf created')
            depo = post_pdf(pdf, thread, self.zenodo_creds)
            self.logger.info('posted pdf')
            self.logger.debug(depo)


        finally:
            pdf.unlink()

        self.reply_completed(response, depo)


    def reply_completed(self, response: tweepy.Response, deposit:Deposition):
        client = tweepy.Client(
            consumer_key=self.creds.api_key,
            consumer_secret=self.creds.api_secret,
            access_token=self.creds.access_token,
            access_token_secret=self.creds.access_secret)
        client.create_tweet(text=f"The preprint of your thread is ready: {deposit.doi_url} - {deposit.title}",
                            in_reply_to_tweet_id=response.data.id)
        self.logger.info('replied')



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
                    ])
        self.logger.debug('stopped')

    def _check_mentioned(self, tweet:tweepy.tweet.Tweet) -> bool:
        """
        check if we are directly mentioned in this tweet
        (as opposed to being mentioned in a reply)
        """
        mentioned_users = [u['username'] == self.username for u in tweet.entities.get('mentions', [])]
        return any(mentioned_users)

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



