from telethon import TelegramClient, events
import logging
import os
from dotenv import load_dotenv
import requests
from aiogram import Bot
import asyncio



api_id = '22456473'
api_hash = 'bdf758a96debbe58f6714bce74eb5834'
phone_number = '+9647720493654'




client = TelegramClient('spotizer_stream/telegram_service/my_session', api_id, api_hash)


# @client.on(events.NewMessage(chats=7894843761))
# async def my_event_handler_sport_chats(event):
#     try:
#         if event.text:
#            print(event.text)
#     except Exception as e:
#         print(str(e))
        # logger.error(f"error:{str(e)}")


async def start_client():
    await client.start()
    print("Client started.")
    await client.run_until_disconnected()
    
if __name__== "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_client())