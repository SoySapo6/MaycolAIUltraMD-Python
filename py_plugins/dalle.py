# py_plugins/dalle.py
import requests
import logging

COMMAND = "dalle"
HELP = "Generates an image from a text prompt using DALL-E.\nUsage: .dalle <prompt>"
TAGS = ['ai', 'tools']

API_URL = "https://nightapi.is-a.dev/api/dalle"

async def execute(m, args):
    """
    Generates an image using the DALL-E API.
    """
    if not args:
        return "Please provide a prompt to generate an image.\nExample: .dalle a cat programming python"

    prompt = " ".join(args)
    await m.reply(f"Generating image for: \"{prompt}\"...")

    try:
        response = requests.get(API_URL, params={'prompt': prompt})
        response.raise_for_status()

        image_data = response.content

        if not image_data:
            return "Error: The API did not return an image."

        image_msg = m.client.build_image_message(
            image_data,
            caption=prompt,
            mime_type="image/jpeg"
        )

        await m.client.send_message(m.chat, message=image_msg)

        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling DALL-E API: {e}")
        return f"Error: Could not connect to the DALL-E API."
    except Exception as e:
        logging.error(f"An unexpected error occurred in the dalle command: {e}")
        return f"An unexpected error occurred: {e}"
