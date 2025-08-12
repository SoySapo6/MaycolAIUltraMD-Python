import requests
from bs4 import BeautifulSoup
import logging

async def ig_stalk(username: str) -> dict:
    """
    Scrapes Instagram user profile data from dumpor.com.

    Args:
        username: The Instagram username to stalk.

    Returns:
        A dictionary containing the user's profile information,
        or an error message if the user is not found or an error occurs.
    """
    username = username.replace('@', '')
    url = f"https://dumpor.com/v/{username}"

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        name_element = soup.find('div', class_='user__title')
        if not name_element:
            return {"error": "User not found or profile is private."}

        name = name_element.find('h1').text.strip()
        uname = name_element.find('h4').text.strip()

        description = soup.find('div', class_='user__info-desc').text.strip()

        profile_pic_style = soup.find('div', class_='user__img')['style']
        profile_pic = profile_pic_style.split("url('")[1].split("')")[0]

        stats = soup.select('#user-page .list__item')
        posts = stats[0].find('span', class_='list__item-count').text.strip()
        followers = stats[1].find('span', class_='list__item-count').text.strip()
        following = stats[2].find('span', class_='list__item-count').text.strip()

        return {
            "name": name,
            "username": uname,
            "description": description,
            "posts": posts,
            "followers": followers,
            "following": following,
            "profile_pic": profile_pic
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Instagram data for {username}: {e}")
        return {"error": "Could not connect to the server."}
    except Exception as e:
        logging.error(f"An error occurred during Instagram scraping for {username}: {e}")
        return {"error": "An unexpected error occurred while parsing the data."}
