export interface Track {
  id: number;
  title: string;
  artist: string;
  file_id: string | null;
  cover_image_url?: string;
}
