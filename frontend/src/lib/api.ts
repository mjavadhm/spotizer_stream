import type { Track } from './types';

const API_BASE_URL = 'https://api.javadhm.online';

export async function fetchTracks(
  id: string,
  type: 'user' | 'playlist'
): Promise<Track[]> {
  let url = '';
  if (type === 'user') {
    url = `${API_BASE_URL}/api/user/${id}/downloads`;
  } else {
    url = `${API_BASE_URL}/api/playlist/${id}`;
  }

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch tracks');
  }

  const data = await response.json();

  // The API response for a playlist might be a Playlist object
  // that contains a 'tracks' array. We'll handle that here.
  if (data.tracks && Array.isArray(data.tracks)) {
    return data.tracks;
  }

  // The user downloads endpoint might return the array directly.
  if (Array.isArray(data)) {
    return data;
  }

  return [];
}
