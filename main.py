import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import json
import os

# Set headers and Telegram bot details
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
TELEGRAM_BOT_TOKEN = '6923200542:AAGamud3gEJXvQKeNcknQ3Is2A7BQzMa8y8'
CHAT_ID = '@asurascansupdates'
UPDATE_CHANNEL_ID = '@asurascansupdates'
URL = 'https://asuracomic.net/manga/?order=update'
SENT_CHAPTERS_FILE = 'sent_chapters.json'

# Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def get_latest_chapters():
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        updates = soup.find_all('div', class_='bsx')

        chapters = []
        for update in updates:
            title_tag = update.find('a', title=True)
            title = title_tag['title']
            link = title_tag['href']
            chapter_tag = update.find('div', class_='epxs')
            chapter = chapter_tag.text.strip()
            image_tag = update.find('img', class_='ts-post-image')
            image_url = image_tag['src'] if image_tag else None

            chapters.append({
                'title': title,
                'chapter': chapter,
                'link': link,
                'image_url': image_url
            })
        return chapters
    except Exception as e:
        print(f"Error fetching chapters: {e}")
        return []

async def get_sent_chapters():
    try:
        if os.path.exists(SENT_CHAPTERS_FILE):
            with open(SENT_CHAPTERS_FILE, 'r') as file:
                sent_chapters = set(tuple(chap) for chap in json.load(file))
        else:
            sent_chapters = set()
        return sent_chapters
    except Exception as e:
        print(f"Error loading sent chapters from file: {e}")
        return set()

async def save_sent_chapters(sent_chapters):
    try:
        with open(SENT_CHAPTERS_FILE, 'w') as file:
            json.dump(list(sent_chapters), file)
    except Exception as e:
        print(f"Error saving sent chapters: {e}")

async def send_telegram_message(chapter_info):
    try:
        message = (
            f"Manhwa: {chapter_info['title']}\n"
            f"Chapter: {chapter_info['chapter']}\n"
            f"Link: {chapter_info['link']}\n"
            f"Enjoy!\n"
            f"By @asurascans Staff"
        )

        if chapter_info['image_url']:
            await bot.send_photo(chat_id=CHAT_ID, photo=chapter_info['image_url'], caption=message)
        else:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')

    except Exception as e:
        print(f"Error sending message: {e}")

async def main_task():
    latest_chapters = await get_latest_chapters()
    sent_chapters = await get_sent_chapters()

    new_chapters = [chapter for chapter in latest_chapters if (chapter['title'], chapter['chapter']) not in sent_chapters]

    for chapter in new_chapters:
        await send_telegram_message(chapter)
        sent_chapters.add((chapter['title'], chapter['chapter']))

    await save_sent_chapters(sent_chapters)

if __name__ == "__main__":
    asyncio.run(main_task())
