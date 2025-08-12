from ..py_lib.scraper import ig_stalk

COMMAND = "igstalk"
HELP = "Stalks an Instagram user and returns their profile info.\nUsage: .igstalk <username>"
TAGS = ['scraper']

async def execute(m, args):
    """
    Stalks an Instagram user and returns their profile info.
    """
    if not args:
        return "Please provide an Instagram username.\nExample: .igstalk anuel"

    username = args[0]
    await m.reply(f"Searching for @{username}'s profile, please wait...")

    data = await ig_stalk(username)

    if data.get("error"):
        return f"Error: {data['error']}"

    response_text = (
        f"👤 *User Profile*\n\n"
        f"▪️ *Name*: {data['name']}\n"
        f"▪️ *Username*: {data['username']}\n"
        f"▪️ *Followers*: {data['followers']}\n"
        f"▪️ *Following*: {data['following']}\n"
        f"▪️ *Posts*: {data['posts']}\n\n"
        f"💬 *Bio*:\n{data['description']}"
    )

    # The neonize library and our simple helpers don't have a sendFile/sendPhotoURL
    # method implemented yet. For now, we just send the text and the URL.
    # A future improvement would be to create a conn.sendFile helper like in the
    # original bot.

    await m.reply(data['profile_pic'])
    return response_text
