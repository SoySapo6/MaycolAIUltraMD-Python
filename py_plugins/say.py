COMMAND = "say"
HELP = "Makes the bot repeat the text you provide.\nUsage: .say <text>"
TAGS = ['tools']

async def execute(m, args):
    """
    Makes the bot say the provided text.
    """
    if not args:
        return "Please provide the text you want me to say."

    text_to_say = ' '.join(args)

    # The original bot prepended a zero-width space. We can do the same.
    # It also handled mentions, which can be added later as we build out
    # more complex message sending helpers.
    final_message = '\u200B' + text_to_say

    return final_message
