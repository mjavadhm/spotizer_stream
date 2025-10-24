from telethon import TelegramClient, events
import logging
import os
from dotenv import load_dotenv
import requests
from aiogram import Bot
import asyncio
import re
from .. import crud
from ..database import get_db


load_dotenv()

api_id = os.getenv("API_ID", '22456473')
api_hash = os.getenv("API_HASH", 'bdf758a96debbe58f6714bce74eb5834')
phone_number = os.getenv("PHONE_NUMBER")


client = TelegramClient('spotizer_stream/telegram_service/my_session', api_id, api_hash)


@client.on(events.NewMessage(from_users='Spotizer_bot', forwards=False))
async def track_handler(event):
    message = event.message
    if message.audio and message.text:
        match = re.match(r'^(\d+)', message.text)
        if match:
            db_id = int(match.group(1))

            saved_message = await client.send_file('me', message.audio, caption=str(db_id))
            telethon_file_id = saved_message.id

            async for db in get_db():
                await crud.update_track_telethon_file_id(db, track_id=db_id, telethon_file_id=str(telethon_file_id))
                break

            print(f"Track {db_id} processed. telethon_file_id: {telethon_file_id}")


async def start_client():
    await client.start()
    print("Client started.")
    await client.run_until_disconnected()
    
if __name__== "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_client())