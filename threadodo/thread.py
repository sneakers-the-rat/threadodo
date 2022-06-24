from threadodo.creds import Creds
import tweepy
import typing
import re
from pathlib import Path
import pypandoc
from dataclasses import dataclass

@dataclass
class Author:
    username: str
    name: str


class Thread:
    def __init__(self,
        tweets: typing.List[tweepy.tweet.Tweet],
        responses: typing.List[tweepy.Response]
    ):
        self.tweets = tweets
        self.responses = responses
        self.pdf = None
        self.sort()

    @property
    def text(self) -> str:
        """
        Text from all the tweets in a thread, double new lines between each

        also replacing any @'s with markdown links to profiles i guess
        """
        text = "\n\n".join([t.text for t in self.tweets])
        # make @'s links
        text = re.sub(r"@([\w\d_]{1,})", r"[@\1](https://twitter.com/\1)", text)
        return text

    @property
    def author(self) -> Author:
        return Author(
            "@" + self.responses[0].includes['users'][0].username,
            self.responses[0].includes['users'][0].name,

        )

    @property
    def title(self) -> str:
        return f"{self.author.name}'s thread - {self.tweets[0].created_at.strftime('%y-%m-%d %H:%M')}"

    def sort(self):
        """
        sort order of tweets
        """
        self.tweets = sorted(self.tweets, key=lambda x: x.created_at)
        self.responses = sorted(self.responses, key=lambda x: x.data.created_at)


    def to_pdf(self, output_file:typing.Optional[Path]=None,
               ) -> Path:
        if output_file is None:
            output_file = Path('.') / f"{self.tweets[0].author_id}_{self.tweets[0].created_at.isoformat()}.pdf"

        pypandoc.convert_text(
            self.text, to="html", format="md",
            outputfile=str(output_file),
            extra_args = [
                '--pdf-engine=weasyprint',
                f'--data-dir={Path(__file__).parent}',
                '--template=./template.html',
            ])
        self.pdf = output_file
        return output_file


    @classmethod
    def from_tweet(cls,
               creds:Creds,
               response:tweepy.Response,
               limit:int=100) -> 'Thread':
        """
        Starting with the mentioned tweet, get all of the tweets in a thread in order
        """
        tweet = response.data
        client = tweepy.Client(creds.bearer_token)
        tweets = [tweet]
        responses = [response]
        while tweet.referenced_tweets is not None and len(tweet.referenced_tweets)>0 and len(tweets)<=limit:
            replied = [t.id for t in tweet.referenced_tweets if t.type=="replied_to"]
            if len(replied)==0:
                # top tweet was qt
                break
            replied = replied[0]
            response = client.get_tweet(id=replied, tweet_fields=[
                "referenced_tweets",
                "author_id",
                "created_at"
            ], expansions=[
                'author_id'
            ])
            tweet = response.data
            tweets.append(tweet)
            responses.append(response)

        return Thread(tweets, responses)
