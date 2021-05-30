from scuffed_bot.exceptions import ArgParseError


async def parse_args(message, required_arguments):
    msg_args = {}
    for word in message.split(" "):
        if ":" in word:
            k, v = word.split(":")
            msg_args[k] = v
    arg_keys = msg_args.keys()
    for arg in required_arguments:
        if arg not in arg_keys:
            raise ArgParseError(f"Required argument \"{arg}\" is missing!")
    return msg_args
