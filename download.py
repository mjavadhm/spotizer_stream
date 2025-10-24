from .telegram_service.telethon_bot import client
import asyncio

async def download_track(deezer_id: str):
    await client.send_message('Spotizer_bot', f'https://www.deezer.com/us/track/{deezer_id}')
    
    
async def download_multiple_tracks(deezer_ids: list):
    
    for i, deezer_id in enumerate(deezer_ids):
        await download_track(deezer_id)
        if (i + 1) % 4 == 0 and (i + 1) < len(deezer_ids):
            await asyncio.sleep(60)
            
async def get_multiple_tracks(deezer_ids: list):
    
    for i, deezer_id in enumerate(deezer_ids):
        await download_track(deezer_id)
        await asyncio.sleep(3)