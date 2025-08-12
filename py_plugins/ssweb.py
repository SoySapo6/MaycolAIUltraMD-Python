# py_plugins/ssweb.py
import requests
import logging

COMMAND = "ssweb"
HELP = "Takes a screenshot of a website.\nUsage: .ssweb <url>"
TAGS = ['tools']

API_URL = "https://nightapi.is-a.dev/api/ssweb"

async def execute(m, args):
    """
    Takes a screenshot of a website using an API.
    """
    if not args:
        return "Please provide a URL.\nExample: .ssweb https://google.com"

    url = args[0]
    await m.reply(f"Taking a screenshot of {url}...")

    try:
        response = requests.get(API_URL, params={'url': url})
        response.raise_for_status()

        # The API returns the image data directly
        image_data = response.content

        if not image_data:
            return "Error: The API did not return an image."

        # Build and send the image message
        # Assuming the image is jpeg. A better implementation might check the
        # 'Content-Type' header of the response.
        image_msg = m.client.build_image_message(
            image_data,
            caption=f"Screenshot of {url}",
            mime_type="image/jpeg"
        )

        await m.client.send_message(m.chat, message=image_msg)

        return None # Don't send a text reply

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling ssweb API: {e}")
        return f"Error: Could not connect to the screenshot API."
    except Exception as e:
        logging.error(f"An unexpected error occurred in the ssweb command: {e}")
        return f"An unexpected error occurred: {e}"
