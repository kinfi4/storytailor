import React from 'react';

interface AudioPlayerProps {
  src: string;
}

function formatTime(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, '0')}`;
}

export default function AudioPlayer({ src }: AudioPlayerProps): JSX.Element {
  const audioRef = React.useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [current, setCurrent] = React.useState(0);
  const [duration, setDuration] = React.useState(0);
  const [volume, setVolume] = React.useState(1);

  React.useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onLoaded = () => setDuration(audio.duration || 0);
    const onTime = () => setCurrent(audio.currentTime || 0);
    const onEnded = () => setIsPlaying(false);
    const onPause = () => setIsPlaying(false);
    const onPlay = () => setIsPlaying(true);
    audio.addEventListener('loadedmetadata', onLoaded);
    audio.addEventListener('timeupdate', onTime);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('pause', onPause);
    audio.addEventListener('play', onPlay);
    return () => {
      audio.removeEventListener('loadedmetadata', onLoaded);
      audio.removeEventListener('timeupdate', onTime);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('pause', onPause);
      audio.removeEventListener('play', onPlay);
    };
  }, []);

  return (
    <div className={`audio-player ${isPlaying ? 'playing' : ''}`}
      aria-label="Audio player"
    >
      <audio ref={audioRef} src={src} preload="metadata" />
      <button
        type="button"
        className="audio-btn"
        onClick={() => {
          const audio = audioRef.current;
          if (!audio) return;
          if (isPlaying) {
            audio.pause();
            setIsPlaying(false);
          } else {
            void audio.play();
            setIsPlaying(true);
          }
        }}
        aria-label={isPlaying ? 'Pause' : 'Play'}
      >
        {isPlaying ? '❚❚' : '►'}
      </button>
      <div className="audio-time" aria-live="polite">{formatTime(current)} / {formatTime(duration)}</div>
      <input
        className="audio-seek range"
        type="range"
        min={0}
        max={Math.max(1, duration)}
        value={current}
        style={{
          background: `linear-gradient(to right, var(--primary-600) ${duration ? (current / duration) * 100 : 0}%, rgba(255,255,255,0.14) ${duration ? (current / duration) * 100 : 0}%)`
        }}
        onChange={(e) => {
          const audio = audioRef.current;
          if (!audio) return;
          const t = Number(e.target.value);
          audio.currentTime = t;
          setCurrent(t);
        }}
      />
      <div className="audio-vol">
        <span className="audio-vol-ico">🔊</span>
        <input
          className="range"
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={volume}
          onChange={(e) => {
            const v = Number(e.target.value);
            setVolume(v);
            if (audioRef.current) audioRef.current.volume = v;
          }}
        />
      </div>
      {isPlaying && (
        <span className="audio-eq" aria-hidden>
          <i />
          <i />
          <i />
        </span>
      )}
    </div>
  );
}


