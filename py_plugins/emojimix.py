# py_plugins/emojimix.py
import requests
import logging

COMMAND = "emojimix"
HELP = "Mixes two emojis into a new one.\nUsage: .emojimix <emoji1> <emoji2>"
TAGS = ['fun', 'tools']

API_URL = "https://nightapi.is-a.dev/api/emojimix"

async def execute(m, args):
    """
    Mixes two emojis using an API.
    """
    if len(args) < 2:
        return "Please provide two emojis to mix.\nExample: .emojimix 😀 🐱"

    emoji1, emoji2 = args[0], args[1]
    await m.reply(f"Mixing {emoji1} and {emoji2}...")

    try:
        response = requests.get(API_URL, params={'emoji1': emoji1, 'emoji2': emoji2})
        response.raise_for_status()

        image_data = response.content

        if not image_data:
            return "Error: The API did not return an image. Are you sure these are valid emojis?"

        # The result is a WEBP. We can send it as a webp image.
        # Some clients might render this as a sticker.
        image_msg = m.client.build_image_message(
            image_data,
            caption=f"{emoji1} + {emoji2}",
            mime_type="image/webp"
        )

        await m.client.send_message(m.chat, message=image_msg)

        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling emojimix API: {e}")
        return f"Error: Could not connect to the emojimix API."
    except Exception as e:
        logging.error(f"An unexpected error occurred in the emojimix command: {e}")
        return f"An unexpected error occurred: {e}"
