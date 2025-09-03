export type StoryFlavor = 'fairy_tale' | 'thriller' | 'romance' | 'science_fiction';
export type StoryStatus =
  | 'just_created'
  | 'generating_story'
  | 'generating_audio'
  | 'completed'
  | 'failed'
  | 'restricted_content_detected';

export interface StoryGenerationRequest {
  flavor: StoryFlavor;
  additionalContext?: string | null;
  // Whether mature content (18+) is allowed. When false, stricter safety applies.
  eightingPlusEnabled?: boolean;
}

export interface StoryGenerationResponse {
  id: string;
  flavor: StoryFlavor;
  title: string;
  storyText: string;
  imageUrl?: string | null;
  audioUrl?: string | null;
  audioDurationSeconds?: number | null;
  generationTimeSeconds?: number | null;
  createdAt: string;
  status: StoryStatus;
}

export interface StoryListItem {
  id: string;
  flavor: StoryFlavor;
  title: string;
  story_preview: string;
  audio_url?: string | null;
  created_at: string;
  status: string;
}

export interface StoryListResponse {
  stories: StoryListItem[];
  total: number;
  page: number;
  page_size: number;
}

export const apiBaseUrl = (() => {
  const urlFromEnv = import.meta.env?.VITE_API_BASE_URL;
  if (urlFromEnv && urlFromEnv.length > 0) return urlFromEnv;
  const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  return `http://${host}:8000`;
})();

export function buildFileUrl(path?: string | null): string | null {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path;
  const clean = path.replace(/^\/?files\/?/, '');
  return `${apiBaseUrl}/api/files/${clean}`;
}

export async function listStories(page = 1, pageSize = 10): Promise<StoryListResponse> {
  const res = await fetch(`${apiBaseUrl}/api/stories?page=${page}&page_size=${pageSize}`);
  if (!res.ok) throw new Error(`Failed to load stories: ${res.status}`);
  return res.json();
}

export async function getStoryById(id: string): Promise<StoryGenerationResponse> {
  const res = await fetch(`${apiBaseUrl}/api/stories/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Failed to load story: ${res.status}`);
  return res.json();
}

export async function generateStory(
  request: StoryGenerationRequest,
  imageFile: File
): Promise<StoryGenerationResponse> {
  const form = new FormData();
  form.append('request', JSON.stringify(request));
  form.append('image', imageFile);

  const res = await fetch(`${apiBaseUrl}/api/stories/generate`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to generate story: ${res.status} ${text}`);
  }
  return res.json();
}

export async function deleteStory(id: string): Promise<void> {
  const res = await fetch(`${apiBaseUrl}/api/stories/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to delete story: ${res.status} ${text}`);
  }
}
