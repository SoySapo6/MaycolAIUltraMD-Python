# py_plugins/gemini.py
import requests
import logging

COMMAND = "gemini"
HELP = "Chat with Gemini AI.\nUsage: .gemini <message>"
TAGS = ['ai']

API_URL = "https://nightapi.is-a.dev/api/gemini"

async def execute(m, args):
    """
    Calls the Gemini API to get a response.
    """
    if not args:
        return "Please provide a message for Gemini.\nExample: .gemini hello"

    message = " ".join(args)

    await m.reply("Thinking...")

    try:
        response = requests.get(API_URL, params={'message': message})
        response.raise_for_status() # Raise an exception for bad status codes

        data = response.json()

        if data.get("status") and data.get("result"):
            return data["result"]
        else:
            logging.error(f"Gemini API returned an unexpected response: {data}")
            return "Error: The API returned an unexpected response."

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Gemini API: {e}")
        return f"Error: Could not connect to the Gemini API. Please try again later."
    except Exception as e:
        logging.error(f"An unexpected error occurred in the gemini command: {e}")
        return f"An unexpected error occurred: {e}"
