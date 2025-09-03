export type StatusStyle = 'info' | 'accent' | 'success' | 'danger' | 'warning';

const STATUS_CONFIG: Record<string, { label: string; style: StatusStyle }> = {
  just_created: { label: 'Queued', style: 'info' },
  generating_story: { label: 'Generating Story', style: 'info' },
  generating_audio: { label: 'Generating Audio', style: 'accent' },
  completed: { label: 'Completed', style: 'success' },
  failed: { label: 'Failed', style: 'danger' },
  audio_too_long: { label: 'Audio is too long', style: 'warning' },
  restricted_content_detected: { label: 'Restricted', style: 'warning' },
};

export function formatStatus(status: string): string {
  return STATUS_CONFIG[status]?.label ?? status.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase());
}

export function statusBadgeClass(status: string): string {
  const style = STATUS_CONFIG[status]?.style ?? 'info';
  return `badge ${style}`;
}


