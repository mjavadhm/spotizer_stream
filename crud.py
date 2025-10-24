import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload

# فایل مدل‌های SQLAlchemy خود را وارد کنید
from . import models

# ------------------- #
# توابع CRUD پلی‌لیست  #
# ------------------- #

async def get_playlist_with_tracks_manual_join(db: AsyncSession, playlist_uuid: uuid.UUID):
    """
    اطلاعات پلی‌لیست و ترک‌های آن را با یک LEFT JOIN از دیتابیس می‌خواند.
    """
    query = (
        select(
            models.Playlists,
            models.PlaylistTracks
        )
        .join(
            models.PlaylistTracks,
            models.Playlists.playlist_id == models.PlaylistTracks.playlist_id,
            isouter=True  # <--- این خط، INNER JOIN را به LEFT JOIN تبدیل می‌کند
        )
        .filter(models.Playlists.uuid == playlist_uuid)
    )
    
    result = await db.execute(query)
    return result.all()
# ----------------------------------- #
# توابع CRUD ترک‌ها (UserDownloads)    #
# ----------------------------------- #

async def get_tracks_by_deezer_ids(
    db: AsyncSession, 
    deezer_ids: List[int], 
    quality: str
) -> List[models.Tracks]:
    """
    جزئیات کامل ترک‌ها را بر اساس لیستی از `deezer_id` و یک کیفیت مشخص به صورت آسنکرون برمی‌گرداند.
    این تابع فقط ترک‌هایی را برمی‌گرداند که با کیفیت مورد نظر در دیتابیس موجود باشند.
    """
    if not deezer_ids:
        return []
        
    query = (
        select(models.Tracks)
        .filter(
            models.Tracks.track_id.in_(deezer_ids),
            models.Tracks.quality == quality
        )
    )
    result = await db.execute(query)
    # .all() لیستی از تمام نتایج را برمی‌گرداند
    return result.scalars().all()


async def get_any_track_info_by_deezer_ids(
    db: AsyncSession, 
    deezer_ids: List[int]
) -> List[models.Tracks]:
    """
    اطلاعات پایه (مانند عنوان و خواننده) ترک‌ها را بر اساس لیستی از `deezer_id`
    از هر کیفیتی که موجود باشد، برمی‌گرداند. این برای زمانی مفید است که ترک با 
    کیفیت مورد نظر هنوز آماده نیست اما می‌خواهیم اطلاعات آن را نمایش دهیم.
    """
    if not deezer_ids:
        return []

    # این کوئری ممکن است برای یک deezer_id چندین کیفیت مختلف را برگرداند.
    # منطق انتخاب یکی از آن‌ها در لایه سرویس (endpoint) انجام می‌شود.
    query = select(models.Tracks).filter(models.Tracks.track_id.in_(deezer_ids))
    result = await db.execute(query)
    return result.scalars().all()


async def update_track_telethon_file_id(db: AsyncSession, track_id: int, telethon_file_id: str):
    """
    Updates the `telethon_file_id` for a given track ID.
    """
    track = await db.get(models.Tracks, track_id)
    if track:
        track.telethon_file_id = telethon_file_id
        await db.commit()
        return track
    return None


async def get_track_by_id(db: AsyncSession, track_id: int) -> Optional[models.Tracks]:
    """
    Retrieves a track by its primary key (ID).
    """
    return await db.get(models.Tracks, track_id)