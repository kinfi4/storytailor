import React from 'react';
import { generateStory, StoryFlavor, StoryGenerationRequest, StoryGenerationResponse } from '../api/client';
import { formatStatus, statusBadgeClass } from '../ui/status';

const FLAVOR_OPTIONS: { value: StoryFlavor; label: string }[] = [
  { value: 'fairy_tale', label: 'Fairy Tale' },
  { value: 'thriller', label: 'Thriller' },
  { value: 'romance', label: 'Romance' },
  { value: 'science_fiction', label: 'Science Fiction' },
];

export default function CreateStoryPage(): JSX.Element {
  const [flavor, setFlavor] = React.useState<StoryFlavor>('fairy_tale');
  const [eightingPlusEnabled, setEightingPlusEnabled] = React.useState<boolean>(false);
  const [additionalContext, setAdditionalContext] = React.useState<string>('');
  const [imageFile, setImageFile] = React.useState<File | null>(null);
  const [result, setResult] = React.useState<StoryGenerationResponse | null>(null);
  const [submitting, setSubmitting] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = React.useState<string | null>(null);

  // custom select state
  const [flavorMenuOpen, setFlavorMenuOpen] = React.useState<boolean>(false);
  const triggerRef = React.useRef<HTMLButtonElement | null>(null);
  const menuRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!flavorMenuOpen) return;
      const t = e.target as Node;
      if (menuRef.current && menuRef.current.contains(t)) return;
      if (triggerRef.current && triggerRef.current.contains(t)) return;
      setFlavorMenuOpen(false);
    }
    function onEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setFlavorMenuOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('keydown', onEsc);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('keydown', onEsc);
    };
  }, [flavorMenuOpen]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!imageFile) {
      setError('Please add an image');
      return;
    }
    setError(null);
    setSubmitting(true);
    setResult(null);
    try {
      const request: StoryGenerationRequest = {
        flavor,
        additionalContext: additionalContext || undefined,
        eightingPlusEnabled,
      };
      const res = await generateStory(request, imageFile);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate story');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h2 className="page-title">Create Story</h2>
      <div className="panel">
        <form onSubmit={onSubmit} className="form">
          <div className="row">
            <label className="label">Flavor</label>
            <div className="select-custom">
              <button
                ref={triggerRef}
                type="button"
                className={`select-trigger ${flavorMenuOpen ? 'open' : ''}`}
                onClick={() => setFlavorMenuOpen((v) => !v)}
                aria-haspopup="listbox"
                aria-expanded={flavorMenuOpen}
              >
                <span className="select-value">{FLAVOR_OPTIONS.find(o => o.value === flavor)?.label}</span>
                <span className="select-caret" aria-hidden>▾</span>
              </button>
              {flavorMenuOpen && (
                <div ref={menuRef} className="select-menu" role="listbox">
                  {FLAVOR_OPTIONS.map((opt) => (
                    <div
                      key={opt.value}
                      role="option"
                      aria-selected={opt.value === flavor}
                      className={`select-option ${opt.value === flavor ? 'selected' : ''}`}
                      onClick={() => {
                        setFlavor(opt.value);
                        setFlavorMenuOpen(false);
                      }}
                    >
                      {opt.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="row">
            <label className="label">Content safety</label>
            <div className="switch">
              <input className="toggle" id="content-safety-toggle" type="checkbox" checked={eightingPlusEnabled} onChange={(e) => setEightingPlusEnabled(e.target.checked)} />
              <label htmlFor="content-safety-toggle" className="switch-label">
                {eightingPlusEnabled ? '18+ allowed' : 'Under-18 safe'}
              </label>
            </div>
          </div>
          <div className="row full">
            <label className="label">Give me more details :)</label>
            <textarea className="textarea" rows={4} value={additionalContext} onChange={(e) => setAdditionalContext(e.target.value)} />
          </div>
          <div className="row full">
            <label className="label">Image</label>
            <div
              className={`dropzone ${imagePreviewUrl ? 'has-image' : ''}`}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const file = e.dataTransfer.files?.[0];
                if (file) {
                  setImageFile(file);
                  setImagePreviewUrl(URL.createObjectURL(file));
                }
              }}
            >
              <input
                id="file-input"
                className="file-input"
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0] || null;
                  setImageFile(file);
                  setImagePreviewUrl(file ? URL.createObjectURL(file) : null);
                }}
              />
              {!imagePreviewUrl && (
                <div className="dropzone-hint">
                  <div className="hint-title">Drop an image here</div>
                  <div className="hint-sub">or click to browse</div>
                </div>
              )}
              {imagePreviewUrl && (
                <img className="dropzone-preview" src={imagePreviewUrl} alt="Selected" />
              )}
            </div>
          </div>
          <div className="footer-actions full">
            <button className="button" type="submit" disabled={submitting}>{submitting ? 'Creating…' : 'Create'}</button>
          </div>
        </form>
      </div>

      {error && <div className="panel" style={{ marginTop: 16 }}><div className="toolbar"><span className="meta" style={{ color: '#ff9b9b' }}>{error}</span></div></div>}

      {result && (
        <div className="panel" style={{ marginTop: 16 }}>
          <div className="card">
            <h3 className="page-title" style={{ fontSize: 20, marginTop: 0 }}>Created</h3>
            <div className="kv">
              <div className="meta">Title</div><div>{result.status === 'completed' ? result.title : 'Story generation in progress...'}</div>
              <div className="meta">Status</div><div><span className={statusBadgeClass(result.status)}>{formatStatus(result.status)}</span></div>
              <div className="meta">Created at</div><div>{new Date(result.createdAt).toLocaleString()}</div>
              {typeof result.generationTimeSeconds === 'number' && (
                <>
                  <div className="meta">Generation time</div>
                  <div>{(() => { const s = Math.round(result.generationTimeSeconds ?? 0); const m = Math.floor(s / 60); const r = s % 60; return m > 0 ? `${m}m ${r}s` : `${r}s`; })()}</div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
