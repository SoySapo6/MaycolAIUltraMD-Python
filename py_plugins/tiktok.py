# py_plugins/tiktok.py
import requests
import logging

COMMAND = "tiktok"
HELP = "Downloads a TikTok video.\nUsage: .tiktok <url>"
TAGS = ['tools']

API_URL = "https://nightapi.is-a.dev/api/tiktok"

async def execute(m, args):
    """
    Downloads a TikTok video using an API.
    """
    if not args:
        return "Please provide a TikTok URL.\nExample: .tiktok https://vm.tiktok.com/..."

    url = args[0]
    await m.reply(f"Downloading TikTok video from {url}...")

    try:
        response = requests.get(API_URL, params={'url': url})
        response.raise_for_status()

        video_data = response.content

        if not video_data:
            return "Error: The API did not return a video."

        # This is an assumption. The user's example was for images.
        # We are assuming a `build_video_message` method exists and works similarly.
        video_msg = m.client.build_video_message(
            video_data,
            caption="Here is your TikTok video!",
            mime_type="video/mp4"
        )

        await m.client.send_message(m.chat, message=video_msg)

        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling TikTok API: {e}")
        return f"Error: Could not connect to the TikTok API."
    except Exception as e:
        logging.error(f"An unexpected error occurred in the tiktok command: {e}")
        return f"An unexpected error occurred: {e}"
