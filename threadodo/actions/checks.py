from threadodo.actions.action import Action, Result
from tweepy import Response

class Check(Action):
    """
    Base class for actions that check something about the tagged message
    to see if we should handle it.
    """


class Mentioned(Check):
    """
    Check that we have been directly mentioned in the message
    """

    def do(self, response:Response) -> Result:
        mentioned_users = [u['username'] == self.bot.username for u in response.data.entities.get('mentions', [])]
        result = Result(ok=any(mentioned_users))
        if not result.ok:
            result.log = "Mentioned, but not directly mentioned"

        return result

