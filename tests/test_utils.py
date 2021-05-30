import scuffed_bot.util as util
from scuffed_bot.exceptions import ArgParseError
import pytest


@pytest.mark.asyncio
async def test_parse_arg_success():
    message = "$test thing:test1 wat:test2 five03:test3"
    required_args = ["thing", "wat"]
    msg_args = await util.parse_args(message, required_args)
    assert msg_args == {"thing": "test1", "wat": "test2", "five03": "test3"}


@pytest.mark.asyncio
async def test_parse_arg_failure():
    message = "$test thing:test1 wat:test2 five03:test3"
    required_args = ["thing", "wat", "test5"]
    with pytest.raises(ArgParseError) as error:
        msg_args = await util.parse_args(message, required_args)
    assert "test5" in str(error)
