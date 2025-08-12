import time

COMMAND = "speed"
HELP = "Measures the bot's response time."
TAGS = ['tools']

async def execute(m, args):
    """
    Calculates the bot's response time.
    `m` is the serialized message object.
    `args` is a list of command arguments.
    """
    start_time = time.monotonic()

    # The "work" is just preparing the response, which is minimal.
    # In a real scenario, this would be the time taken for any task.
    end_time = time.monotonic()

    latency = end_time - start_time

    return f"✰ *¡Pong!*\n> Response Time: {latency:.4f}s"
