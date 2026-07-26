import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import '../../styles/LabyrinthMap.css';

type LabyrinthRoom = {
  x: number;
  y: number;
  event: string | null;
  sources_count: number;
  emission_event: string | null;
  emission_sources_count: number;
  emission_observed_at: string | null;
  updated_at: string;
};

type LabyrinthSummary = {
  total_rooms: number;
  min_x: number | null;
  max_x: number | null;
  min_y: number | null;
  max_y: number | null;
  updated_at: string | null;
  events: Record<string, number>;
};

type Viewport = { centerX: number; centerY: number; span: number };

const MIN_SPAN = 24;
const MAX_SPAN = 140;
const basePath = import.meta.env.VITE_API_URL ?? '';
const apiUrl = (path: string) => `${basePath}${path}`;

const eventColor = (event: string | null): string => {
  if (!event || event === 'unknown') return '#626a75';
  let hash = 0;
  for (const character of event) hash = (hash * 31 + character.charCodeAt(0)) | 0;
  return `hsl(${Math.abs(hash) % 360} 54% 49%)`;
};

const initialViewport = (summary: LabyrinthSummary): Viewport => {
  if (summary.min_x === null || summary.max_x === null || summary.min_y === null || summary.max_y === null) {
    return { centerX: 0, centerY: 0, span: 48 };
  }

  const width = summary.max_x - summary.min_x + 1;
  const height = summary.max_y - summary.min_y + 1;
  return {
    centerX: Math.floor((summary.min_x + summary.max_x) / 2),
    centerY: Math.floor((summary.min_y + summary.max_y) / 2),
    span: Math.max(MIN_SPAN, Math.min(MAX_SPAN, Math.max(width, height))),
  };
};

const LabyrinthMapPage = () => {
  const { t, i18n } = useTranslation();
  const [summary, setSummary] = useState<LabyrinthSummary | null>(null);
  const [viewport, setViewport] = useState<Viewport>({ centerX: 0, centerY: 0, span: 48 });
  const [rooms, setRooms] = useState<LabyrinthRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [mapLoading, setMapLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<LabyrinthSummary>(apiUrl('/api/extension/labyrinth/map/summary'));
      setSummary(response.data);
      setViewport(initialViewport(response.data));
    } catch {
      setError(t('labyrinth.loadError'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  useEffect(() => {
    if (!summary) return;
    const controller = new AbortController();
    const half = Math.floor(viewport.span / 2);
    setMapLoading(true);
    axios.get<{ rooms: LabyrinthRoom[] }>(apiUrl('/api/extension/labyrinth/map'), {
      params: {
        min_x: viewport.centerX - half,
        max_x: viewport.centerX - half + viewport.span - 1,
        min_y: viewport.centerY - half,
        max_y: viewport.centerY - half + viewport.span - 1,
      },
      signal: controller.signal,
    }).then((response) => {
      setRooms(response.data.rooms);
      setError(null);
    }).catch((requestError) => {
      if (!axios.isCancel(requestError)) setError(t('labyrinth.loadError'));
    }).finally(() => {
      if (!controller.signal.aborted) setMapLoading(false);
    });
    return () => controller.abort();
  }, [summary, t, viewport]);

  const move = (x: number, y: number) => {
    const step = Math.max(1, Math.floor(viewport.span * 0.7));
    setViewport((current) => ({ ...current, centerX: current.centerX + x * step, centerY: current.centerY + y * step }));
  };

  const zoom = (direction: 1 | -1) => {
    setViewport((current) => ({
      ...current,
      span: Math.max(MIN_SPAN, Math.min(MAX_SPAN, direction > 0 ? current.span * 2 : Math.floor(current.span / 2))),
    }));
  };

  const minX = viewport.centerX - Math.floor(viewport.span / 2);
  const minY = viewport.centerY - Math.floor(viewport.span / 2);

  if (loading) return <div className="labyrinth-page"><div className="loading">{t('common.loading')}</div></div>;

  return (
    <section className="labyrinth-page">
      <div className="labyrinth-heading">
        <div>
          <h1>{t('labyrinth.title')}</h1>
          <p>{t('labyrinth.description')}</p>
        </div>
        <button type="button" onClick={() => void loadSummary()}>{t('common.refresh')}</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="labyrinth-summary">
        <div><strong>{summary?.total_rooms ?? 0}</strong><span>{t('labyrinth.observedRooms')}</span></div>
        <div><strong>{rooms.length}</strong><span>{t('labyrinth.visibleRooms')}</span></div>
        <div><strong>{summary?.updated_at ? new Intl.DateTimeFormat(i18n.language, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(summary.updated_at)) : '—'}</strong><span>{t('labyrinth.lastUpdate')}</span></div>
      </div>

      <div className="labyrinth-layout">
        <aside className="labyrinth-controls" aria-label={t('labyrinth.navigationLabel')}>
          <div className="labyrinth-coordinates">X: {viewport.centerX}, Y: {viewport.centerY}</div>
          <div className="labyrinth-direction-controls">
            <button type="button" onClick={() => move(0, -1)} aria-label={t('labyrinth.moveUp')}>↑</button>
            <button type="button" onClick={() => move(-1, 0)} aria-label={t('labyrinth.moveLeft')}>←</button>
            <button type="button" onClick={() => summary && setViewport(initialViewport(summary))} aria-label={t('labyrinth.resetView')}>◎</button>
            <button type="button" onClick={() => move(1, 0)} aria-label={t('labyrinth.moveRight')}>→</button>
            <button type="button" onClick={() => move(0, 1)} aria-label={t('labyrinth.moveDown')}>↓</button>
          </div>
          <div className="labyrinth-zoom-controls">
            <button type="button" onClick={() => zoom(-1)} disabled={viewport.span <= MIN_SPAN}>−</button>
            <span>{t('labyrinth.span', { count: viewport.span })}</span>
            <button type="button" onClick={() => zoom(1)} disabled={viewport.span >= MAX_SPAN}>+</button>
          </div>
          <div className="labyrinth-legend">
            <span><i className="legend-room" />{t('labyrinth.room')}</span>
            <span><i className="legend-emission" />{t('labyrinth.emission')}</span>
          </div>
        </aside>

        <div className="labyrinth-map-wrap">
          {mapLoading && <div className="labyrinth-map-loading">{t('common.loading')}</div>}
          <svg className="labyrinth-map" viewBox={`${minX} ${minY} ${viewport.span} ${viewport.span}`} role="img" aria-label={t('labyrinth.mapLabel')}>
            <defs>
              <pattern id="labyrinth-grid" width="1" height="1" patternUnits="userSpaceOnUse">
                <path d="M 1 0 L 0 0 0 1" fill="none" stroke="rgba(255,255,255,.12)" strokeWidth="0.03" />
              </pattern>
            </defs>
            <rect x={minX} y={minY} width={viewport.span} height={viewport.span} fill="url(#labyrinth-grid)" />
            {rooms.map((room) => (
              <g key={`${room.x}:${room.y}`}>
                <title>{`${t('labyrinth.coordinates', { x: room.x, y: room.y })}\n${room.event ?? t('labyrinth.unknown')}${room.emission_event ? `\n${t('labyrinth.emission')}: ${room.emission_event}` : ''}`}</title>
                <rect x={room.x + 0.07} y={room.y + 0.07} width="0.86" height="0.86" rx="0.12" fill={eventColor(room.event)} />
                {room.emission_event && <circle cx={room.x + 0.5} cy={room.y + 0.5} r="0.21" fill="none" stroke="#ffd166" strokeWidth="0.1" />}
              </g>
            ))}
          </svg>
        </div>
      </div>
    </section>
  );
};

export default LabyrinthMapPage;
