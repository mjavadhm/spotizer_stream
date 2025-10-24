from typing import Optional
import datetime
import uuid as uuidlib
import enum

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, SmallInteger, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLAlchemyEnum

class Base(DeclarativeBase):
    pass


class Tracks(Base):
    __tablename__ = 'tracks'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tracks_pkey'),
        Index('idx_tracks_downloads', 'download_count')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quality: Mapped[str] = mapped_column(String(16), nullable=False)
    track_id: Mapped[Optional[str]] = mapped_column(String(64))
    url: Mapped[Optional[str]] = mapped_column(Text)
    file_id: Mapped[Optional[str]] = mapped_column(Text)
    telethon_file_id: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    artist: Mapped[Optional[str]] = mapped_column(String(255))
    album: Mapped[Optional[str]] = mapped_column(String(255))
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    download_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    last_downloaded: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    file_name: Mapped[Optional[str]] = mapped_column(Text)
    content_type: Mapped[Optional[str]] = mapped_column(String(64))


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='users_pkey'),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_bot: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    language_code: Mapped[Optional[str]] = mapped_column(String(10))
    is_premium: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    added_to_attachment_menu: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    can_join_groups: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    can_read_all_group_messages: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    supports_inline_queries: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    last_activity: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    messages: Mapped[list['Messages']] = relationship('Messages', back_populates='user')
    playlists: Mapped[list['Playlists']] = relationship('Playlists', back_populates='user')
    user_activity: Mapped[list['UserActivity']] = relationship('UserActivity', back_populates='user')
    user_downloads: Mapped[list['UserDownloads']] = relationship('UserDownloads', back_populates='user')


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', name='messages_user_id_fkey'),
        PrimaryKeyConstraint('message_id', name='messages_pkey')
    )

    message_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    message_text: Mapped[Optional[str]] = mapped_column(Text)
    message_type: Mapped[Optional[str]] = mapped_column(String(50))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    sent_by: Mapped[Optional[int]] = mapped_column(SmallInteger)
    media: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='messages')


class Playlists(Base):
    __tablename__ = 'playlists'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', name='playlists_user_id_fkey'),
        PrimaryKeyConstraint('playlist_id', name='playlists_pkey'),
        UniqueConstraint('user_id', 'name', name='playlists_user_id_name_key'),
        UniqueConstraint('uuid', name='playlists_uuid_key')
    )

    playlist_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    uuid: Mapped[Optional[uuidlib.UUID]] = mapped_column(Uuid, server_default=text('uuid_generate_v4()'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='playlists')
    playlist_tracks: Mapped[list['PlaylistTracks']] = relationship('PlaylistTracks', back_populates='playlist')


class UserActivity(Base):
    __tablename__ = 'user_activity'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', name='user_activity_user_id_fkey'),
        PrimaryKeyConstraint('activity_id', name='user_activity_pkey')
    )

    activity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='user_activity')


class UserDownloads(Base):
    __tablename__ = 'user_downloads'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', name='user_downloads_user_id_fkey'),
        PrimaryKeyConstraint('download_id', name='user_downloads_pkey'),
        UniqueConstraint('deezer_id', 'content_type', 'quality', name='user_content_unique'),
        Index('idx_downloads_timestamp', 'downloaded_at'),
        Index('idx_downloads_user_id', 'user_id')
    )

    download_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deezer_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_id: Mapped[str] = mapped_column(Text, nullable=False)
    quality: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    url: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    artist: Mapped[Optional[str]] = mapped_column(String(255))
    album: Mapped[Optional[str]] = mapped_column(String(255))
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    downloaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    file_name: Mapped[Optional[str]] = mapped_column(Text)
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='user_downloads')


class UserSettings(Users):
    __tablename__ = 'user_settings'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', name='user_settings_user_id_fkey'),
        PrimaryKeyConstraint('user_id', name='user_settings_pkey')
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    download_quality: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'MP3_320'::character varying"))
    make_zip: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    language: Mapped[Optional[str]] = mapped_column(String(10), server_default=text("'en'::character varying"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class PlaylistTracks(Base):
    __tablename__ = 'playlist_tracks'
    __table_args__ = (
        ForeignKeyConstraint(['playlist_id'], ['playlists.playlist_id'], ondelete='CASCADE', name='playlist_tracks_playlist_id_fkey'),
        PrimaryKeyConstraint('playlist_track_id', name='playlist_tracks_pkey')
    )

    playlist_track_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    track_deezer_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    playlist_id: Mapped[Optional[int]] = mapped_column(Integer)
    added_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    playlist: Mapped[Optional['Playlists']] = relationship('Playlists', back_populates='playlist_tracks')
