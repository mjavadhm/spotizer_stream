from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from . import crud, schemas
from .database import get_db
import asyncio
from .download import download_multiple_tracks, get_multiple_tracks
from .telegram_service.telethon_bot import client
import httpx
from aiogram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
DOWNLOADING_TRACKS = []
BOT_TOKEN=os.getenv("s")
bot = Bot(token=BOT_TOKEN)

origins = [
    "https://javadhm.online",
]

# --- 3. Add the middleware to your app ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    """
    This function will be called when the FastAPI application starts.
    It connects the Telethon client.
    """
    await client.start()
    print("Telethon client has connected successfully.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    This function will be called when the FastAPI application stops.
    It disconnects the Telethon client gracefully.
    """
    await client.disconnect()
    print("Telethon client has disconnected.")

async def _process_tracks(db: AsyncSession, track_deezer_ids: list[str]) -> list[schemas.Track]:
    """
    Helper function to process a list of track Deezer IDs.
    """
    target_quality = "MP3_128"
    ready_tracks = await crud.get_tracks_by_deezer_ids(db, deezer_ids=track_deezer_ids, quality=target_quality)
    ready_tracks_map = {track.track_id: track for track in ready_tracks}

    base_info_tracks = await crud.get_any_track_info_by_deezer_ids(db, deezer_ids=track_deezer_ids)
    base_info_map = {track.track_id: track for track in base_info_tracks}

    final_tracks_list = []
    download_needed_tracks = []
    for track_id_str in track_deezer_ids:
        if track_id_str in ready_tracks_map:
            track_data = ready_tracks_map[track_id_str]
            final_tracks_list.append(schemas.Track(
                id=track_data.id,
                title=track_data.title,
                artist=track_data.artist,
                duration=track_data.duration,
                file_id=track_data.file_id,
                telethon_file_id=track_data.telethon_file_id
            ))
        elif track_id_str in base_info_map:
            track_data = base_info_map[track_id_str]
            final_tracks_list.append(schemas.Track(
                id=track_data.id,
                title=track_data.title,
                artist=track_data.artist,
                duration=track_data.duration,
                file_id=None,
                telethon_file_id=None
            ))
            if track_id_str not in DOWNLOADING_TRACKS:
                download_needed_tracks.append(track_id_str)

    if download_needed_tracks:
        for track_id in download_needed_tracks:
            DOWNLOADING_TRACKS.append(track_id)
        asyncio.create_task(download_multiple_tracks(download_needed_tracks))

    tracks_to_forward = [track for track in ready_tracks if not track.telethon_file_id]
    if tracks_to_forward:
        asyncio.create_task(forward_tracks_to_telethon(tracks_to_forward))

    return final_tracks_list

@app.get("/api/playlist/{playlist_uuid}", response_model=schemas.Playlist)
async def read_playlist(playlist_uuid: uuid.UUID, db: AsyncSession = Depends(get_db)):

    query_results = await crud.get_playlist_with_tracks_manual_join(db, playlist_uuid=playlist_uuid)
    print(f"Query Results: {query_results}")
    # اگر نتیجه خالی بود، یعنی یا پلی‌لیست وجود ندارد یا ترکی در آن نیست
    if not query_results:
        # برای ارائه پاسخ بهتر، می‌توانیم چک کنیم که آیا پلی‌لیست اصلاً وجود دارد یا نه
        # اما برای سادگی، فعلاً خطای 404 برمی‌گردانیم
        raise HTTPException(status_code=404, detail="Playlist not found or it is empty")

    # ۲. استخراج اطلاعات پلی‌لیست و deezer_id ها
    # اطلاعات پلی‌لیست در تمام ردیف‌ها یکسان است، پس از ردیف اول استفاده می‌کنیم
    playlist = query_results[0][0]  # [0] برای ردیف اول، [0] برای آبجکت Playlists

    # deezer_id ها را از تمام ردیف‌ها استخراج می‌کنیم
    track_deezer_ids = [row[1].track_deezer_id for row in query_results if row[1] is not None]
    str_track_ids = [str(tid) for tid in track_deezer_ids]
    print(f"Extracted Deezer IDs: {str_track_ids}")
    if not str_track_ids:
        return schemas.Playlist(
            playlist_name=playlist.name,
            description=playlist.description,
            tracks=[]
        )

    final_tracks_list = await _process_tracks(db, str_track_ids)

    return schemas.Playlist(
        playlist_name=playlist.name,
        description=playlist.description,
        tracks=final_tracks_list
    )


async def forward_tracks_to_telethon(tracks: list):
    """
    Forwards tracks to the Telethon user using the Aiogram bot.
    """
    for track in tracks:
        try:
            await bot.send_audio(
                chat_id=7631847071,
                audio=track.file_id,
                caption=str(track.id)
            )
            await asyncio.sleep(1)  # Avoid rate limiting
        except Exception as e:
            print(f"Error forwarding track {track.id} to Telethon user: {e}")
    
    
@app.get("/stream/track/{track_id}")
async def stream_track(track_id: int, db: AsyncSession = Depends(get_db)):
    """
    Streams a track by its database ID.
    It automatically determines whether to use Telethon or the Bot API.
    """
    track = await crud.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if track.quality == 'FLAC':
        media_type = 'audio/flac'
    else:
        media_type = 'audio/mpeg'

    async def telethon_file_iterator(file_id):
        try:
            message_id = int(file_id)
            message = await client.get_messages('@Spotizer_bot', ids=message_id)
            if message and message.audio:
                async for chunk in client.iter_download(message.audio):
                    yield chunk
            else:
                print(f"Telethon message {file_id} not found or not an audio file.")
                yield b''
        except Exception as e:
            print(f"An error occurred during Telethon streaming: {e}")
            yield b''

    async def bot_api_file_iterator(file_id):
        try:
            file_info = await bot.get_file(file_id)
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
            
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        yield chunk
        except httpx.HTTPStatusError as e:
            print(f"Error fetching file from Telegram Bot API: {e.response.status_code}")
        except Exception as e:
            print(f"An error occurred during Bot API streaming proxy: {e}")

    if track.telethon_file_id:
        return StreamingResponse(telethon_file_iterator(track.telethon_file_id), media_type=media_type)
    elif track.file_id:
        return StreamingResponse(bot_api_file_iterator(track.file_id), media_type=media_type)
    else:
        raise HTTPException(status_code=404, detail="Track has no file ID")


@app.get("/api/user/{user_id}/downloads", response_model=schemas.UserDownloadsResponse)
async def get_user_downloads_endpoint(user_id: int, page: int = 1, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a paginated list of a user's downloaded tracks.
    """
    limit = 10
    user_downloads = await crud.get_user_downloads(db, user_id=user_id, page=page, limit=limit)
    total_tracks = await crud.count_user_downloads(db, user_id=user_id)

    if not user_downloads:
        return schemas.UserDownloadsResponse(page=page, limit=limit, total_tracks=total_tracks, tracks=[])

    track_deezer_ids = [str(download.deezer_id) for download in user_downloads]

    final_tracks_list = await _process_tracks(db, track_deezer_ids)

    return schemas.UserDownloadsResponse(
        page=page,
        limit=limit,
        total_tracks=total_tracks,
        tracks=final_tracks_list
    )
