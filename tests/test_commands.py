from threadodo.bot import Threadodo
from threadodo.actions import commands
import pytest
from tweepy import Tweet, StreamResponse


@pytest.mark.parametrize(
    ['test_str', 'test_res'],
    [
        (
            '@threadodo_bot identify\nname: Myname T. Identifier\norcid: 101001010101010',
            {'username': 'threadodo_bot', 'command': 'identify',
             'args': {
                 'name': 'Myname T. Identifier',
                 'orcid': '101001010101010'
             }}
        )
    ] )

def test_parse_identity(test_str, test_res):
    bot = Threadodo()
    response = StreamResponse(Tweet({'text':test_str, 'id':'1095'}), {}, {}, {})
    id = commands.Identify(bot)

    assert id.check(response)

    params = id.parse(response)

    assert params.__dict__ == test_res