# A simple test plugin

COMMAND = "ping"
HELP = "Responds with 'pong!' to check if the bot is alive."
TAGS = ['tools']

async def execute(m, args):
    """
    A simple ping command. Returns 'pong!' and can echo arguments.
    `m` is the serialized message object.
    `args` is a list of command arguments.
    """
    if args:
        return f"pong! (echo: {' '.join(args)})"
    return "pong!"
