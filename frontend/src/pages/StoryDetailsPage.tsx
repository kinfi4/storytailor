import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiBaseUrl, buildFileUrl, deleteStory, getStoryById, StoryGenerationResponse } from '../api/client';
import { formatStatus, statusBadgeClass } from '../ui/status';
import AudioPlayer from '../ui/AudioPlayer';

export default function StoryDetailsPage(): JSX.Element {
  const { id } = useParams();
  const navigate = useNavigate();
  const [story, setStory] = React.useState<StoryGenerationResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);
  const [deleting, setDeleting] = React.useState<boolean>(false);

  React.useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getStoryById(id);
        setStory(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (!id) return <p>Missing id</p>;
  if (loading) return <p>Loading...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!story) return <p>No story found</p>;

  return (
    <div>
      <h2 className="page-title">{story.title}</h2>
      <div className="panel">
        <div className="toolbar" style={{ marginBottom: 10 }}>
          <button
            className="button danger"
            disabled={deleting}
            onClick={async () => {
              if (!id) return;
              if (!confirm('Delete this story?')) return;
              try {
                setDeleting(true);
                await deleteStory(id);
                navigate('/stories');
              } catch (err: unknown) {
                setError(err instanceof Error ? err.message : 'Failed to delete');
              } finally {
                setDeleting(false);
              }
            }}
          >
            {deleting ? 'Deleting…' : 'Delete'}
          </button>
        </div>
        <div className="card">
          {story.imageUrl && (
            <div className="image-frame">
              <div className="image-glow" />
              <img className="image" src={buildFileUrl(story.imageUrl) ?? ''} alt="Uploaded" />
            </div>
          )}
          <div className="kv">
            <div className="meta">Flavor</div><div style={{ textTransform: 'capitalize' }}>{story.flavor.replace('_', ' ')}</div>
            <div className="meta">Status</div><div><span className={statusBadgeClass(story.status)}>{formatStatus(story.status)}</span></div>
            <div className="meta">Created</div><div>{new Date(story.createdAt).toLocaleString()}</div>
            {typeof story.generationTimeSeconds === 'number' && (
              <>
                <div className="meta">Generation time</div>
                <div>{(() => { const s = Math.round(story.generationTimeSeconds ?? 0); const m = Math.floor(s / 60); const r = s % 60; return m > 0 ? `${m}m ${r}s` : `${r}s`; })()}</div>
              </>
            )}
          </div>
          {story.audioUrl && (
            <div style={{ marginTop: 16 }}>
              <AudioPlayer src={buildFileUrl(story.audioUrl) ?? ''} />
              {story.audioDurationSeconds != null && (
                <div className="meta" style={{ marginTop: 6 }}>
                  Audio duration: {Math.round(story.audioDurationSeconds)}s
                </div>
              )}
            </div>
          )}
          <h3 className="page-title" style={{ fontSize: 20, marginTop: 22 }}>Story Text</h3>
          <pre className="pre">{story.storyText}</pre>
        </div>
      </div>
    </div>
  );
}
