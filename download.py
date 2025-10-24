from .telegram_service.telethon_bot import client
import asyncio

async def download_track(deezer_id: str, db_id: int):
    await client.send_message('Spotizer_bot', f'{db_id} https://www.deezer.com/us/track/{deezer_id}')
    
    
async def download_multiple_tracks(tracks: list):
    
    for i, track in enumerate(tracks):
        await download_track(track.track_id, track.id)
        if (i + 1) % 4 == 0 and (i + 1) < len(tracks):
            await asyncio.sleep(60)
            
async def get_multiple_tracks(deezer_ids: list):
    
    for i, deezer_id in enumerate(deezer_ids):
        await download_track(deezer_id)
        await asyncio.sleep(3)