# py_plugins/simi.py
import requests
import logging

COMMAND = "simi"
HELP = "Chat with SimSimi.\nUsage: .simi <message>"
TAGS = ['ai']

API_URL = "https://nightapi.is-a.dev/api/simi"

async def execute(m, args):
    """
    Calls the SimSimi API to get a response.
    """
    if not args:
        return "Please provide a message for Simi.\nExample: .simi hello"

    message = " ".join(args)

    await m.reply("...")

    try:
        # The API seems to require a language parameter, defaulting to 'en'
        params = {'text': message, 'language': 'en'}
        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("success") and data.get("response"):
            return data["response"]
        else:
            logging.error(f"Simi API returned an unexpected response: {data}")
            return "Error: The API returned an unexpected response."

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Simi API: {e}")
        return f"Error: Could not connect to the Simi API. Please try again later."
    except Exception as e:
        logging.error(f"An unexpected error occurred in the simi command: {e}")
        return f"An unexpected error occurred: {e}"
