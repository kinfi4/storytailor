import React from 'react';
import { Link } from 'react-router-dom';
import { listStories, deleteStory, StoryListItem } from '../api/client';
import { formatStatus, statusBadgeClass } from '../ui/status';

export default function StoriesListPage(): JSX.Element {
  const [stories, setStories] = React.useState<StoryListItem[]>([]);
  const [page, setPage] = React.useState<number>(1);
  const [pageSize, setPageSize] = React.useState<number>(10);
  const [total, setTotal] = React.useState<number>(0);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);
  const [deletingId, setDeletingId] = React.useState<string | null>(null);

  // custom select for page size
  const [psMenuOpen, setPsMenuOpen] = React.useState<boolean>(false);
  const psTriggerRef = React.useRef<HTMLButtonElement | null>(null);
  const psMenuRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!psMenuOpen) return;
      const t = e.target as Node;
      if (psMenuRef.current && psMenuRef.current.contains(t)) return;
      if (psTriggerRef.current && psTriggerRef.current.contains(t)) return;
      setPsMenuOpen(false);
    }
    function onEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setPsMenuOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('keydown', onEsc);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('keydown', onEsc);
    };
  }, [psMenuOpen]);

  const load = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listStories(page, pageSize);
      setStories(data.stories);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize]);

  React.useEffect(() => {
    void load();
  }, [load]);

  const onDelete = async (id: string) => {
    if (!confirm('Delete this story?')) return;
    try {
      setDeletingId(id);
      await deleteStory(id);
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    } finally {
      setDeletingId(null);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <h2 className="page-title">Stories Archive</h2>
      <div className="panel">
        <div className="toolbar">
          <button className="button ghost" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>
            Prev
          </button>
          <span className="meta">Page {page} / {totalPages}</span>
          <button className="button ghost" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
            Next
          </button>
          <span className="meta" style={{ marginLeft: 'auto' }}>Page size</span>
          <div className="select-custom" style={{ width: 110 }}>
            <button
              ref={psTriggerRef}
              type="button"
              className={`select-trigger ${psMenuOpen ? 'open' : ''}`}
              onClick={() => setPsMenuOpen((v) => !v)}
              aria-haspopup="listbox"
              aria-expanded={psMenuOpen}
            >
              <span className="select-value">{pageSize}</span>
              <span className="select-caret" aria-hidden>▾</span>
            </button>
            {psMenuOpen && (
              <div ref={psMenuRef} className="select-menu" role="listbox">
                {[5, 10, 20, 50].map((s) => (
                  <div
                    key={s}
                    role="option"
                    aria-selected={s === pageSize}
                    className={`select-option ${s === pageSize ? 'selected' : ''}`}
                    onClick={() => { setPageSize(s); setPsMenuOpen(false); }}
                  >
                    {s}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        {loading && <div className="toolbar"><span className="meta">Loading…</span></div>}
        {error && <div className="toolbar"><span className="meta" style={{ color: '#ff9b9b' }}>{error}</span></div>}
        <ul className="list">
          {stories.map((s) => (
            <li key={s.id} className="item">
              <Link to={`/stories/${s.id}`}>
                <div className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <strong>{s.title}</strong>
                    <span className={statusBadgeClass(s.status)}>{formatStatus(s.status)}</span>
                  </div>
                  <div className="meta" style={{ marginTop: 6 }}>{new Date(s.created_at).toLocaleString()}</div>
                  <div style={{ marginTop: 10 }}>{s.story_preview}</div>
                </div>
              </Link>
              <div className="toolbar" style={{ marginTop: 6 }}>
                <button
                  className="button danger"
                  onClick={() => { void onDelete(s.id); }}
                  disabled={deletingId === s.id}
                >
                  {deletingId === s.id ? 'Deleting…' : 'Delete'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
