from pydantic import BaseModel
from typing import List, Optional

class Track(BaseModel):
    title: str
    artist: str
    duration: int
    file_id: Optional[str] = None
    telethon_file_id: Optional[str] = None

class Playlist(BaseModel):
    playlist_name: str
    description: Optional[str] = None
    tracks: List[Track]