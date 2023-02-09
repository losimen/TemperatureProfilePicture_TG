import asyncio
import requests
import datetime
import logging

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client
from io import BytesIO


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename='logs.txt')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_bio():
    x = requests.get('https://api.open-meteo.com/v1/forecast?latitude=50.45&longitude=30.52&hourly=temperature_2m')

    temperature = x.json()['hourly']['temperature_2m'][0]
    for time in x.json()['hourly']['time']:
        convert_time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M')
        now_time = datetime.datetime.now()

        if convert_time.hour == now_time.hour and convert_time.day == now_time.day and convert_time.month == now_time.month and convert_time.year == now_time.year:
            temperature = x.json()['hourly']['temperature_2m'][x.json()['hourly']['time'].index(time)]
            break

    table = Image.open('table.png')
    draw = ImageDraw.Draw(table)
    font = ImageFont.truetype("Verdana.ttf", 98)

    _, _, w, h = draw.textbbox((0, 0), f"{temperature}°C", font=font)
    draw.text(((640 - w) / 2, (640 - h) / 2), f"{temperature}°C", font=font, fill='white')

    bio = BytesIO()
    bio.name = 'test.png'
    table.save(bio, 'PNG')
    bio.seek(0)
    return bio


async def scheduler_work(app):
    try:
        async with app:
            photos = [p async for p in app.get_chat_photos("me")]
            await app.delete_profile_photos(photos[0].file_id)
            await app.set_profile_photo(photo=get_bio())
            logger.debug("Profile photo updated!")

    except Exception as e:
        logger.debug(e)


async def main():
    app = Client("my_account")
    logger.debug("Bot started!")

    while True:
        await scheduler_work(app)
        await asyncio.sleep(60)


asyncio.run(main())
print("Bot stopped!")
