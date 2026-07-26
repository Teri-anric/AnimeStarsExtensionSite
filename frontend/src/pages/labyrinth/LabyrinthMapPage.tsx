import { useCallback, useEffect, useRef, useState } from 'react';
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
  if (!event || event === 'unknown') return '#445066';
  if (event.includes('boss')) return '#b84c5a';
  if (event.includes('trap')) return '#a85c78';
  if (event.includes('mine') || event.includes('gift') || event.includes('chest')) return '#b98736';
  if (event.includes('recovery') || event.includes('luck')) return '#3c9976';
  if (event.includes('relic') || event.includes('resonance')) return '#7359ad';
  if (event.includes('trader')) return '#3d7eaf';
  let hash = 0;
  for (const character of event) hash = (hash * 31 + character.charCodeAt(0)) | 0;
  return `hsl(${Math.abs(hash) % 360} 54% 49%)`;
};

const eventIcon = (event: string | null): string => {
  if (!event) return '·';
  if (event.includes('hard_boss')) return '☠';
  if (event.includes('boss')) return '👹';
  if (event.includes('trap')) return '⚠';
  if (event.includes('mine')) return '⛏';
  if (event.includes('gift') || event.includes('chest')) return '🎁';
  if (event.includes('recovery')) return '♥';
  if (event.includes('luck')) return '♣';
  if (event.includes('relic')) return '◈';
  if (event.includes('trader')) return '🛒';
  if (event.includes('quiz')) return '?';
  return '✦';
};

const initialViewport = (summary: LabyrinthSummary): Viewport => {
  if (summary.min_x === null || summary.max_x === null || summary.min_y === null || summary.max_y === null) {
    return { centerX: 0, centerY: 0, span: 48 };
  }

  return {
    centerX: Math.floor((summary.min_x + summary.max_x) / 2),
    centerY: Math.floor((summary.min_y + summary.max_y) / 2),
    span: 25,
  };
};

const LabyrinthMapPage = () => {
  const { t, i18n } = useTranslation();
  const [summary, setSummary] = useState<LabyrinthSummary | null>(null);
  const [viewport, setViewport] = useState<Viewport>({ centerX: 0, centerY: 0, span: 48 });
  const [rooms, setRooms] = useState<LabyrinthRoom[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<LabyrinthRoom | null>(null);
  const [loading, setLoading] = useState(true);
  const [mapLoading, setMapLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dragStart = useRef<{ x: number; y: number; centerX: number; centerY: number } | null>(null);
  const dragMoved = useRef(false);

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
      setSelectedRoom((current) => response.data.rooms.find((room) => room.x === current?.x && room.y === current?.y) ?? null);
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

  const onPointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
    dragStart.current = { x: event.clientX, y: event.clientY, centerX: viewport.centerX, centerY: viewport.centerY };
    dragMoved.current = false;
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
    const start = dragStart.current;
    if (!start) return;
    if (Math.abs(start.x - event.clientX) > 3 || Math.abs(start.y - event.clientY) > 3) dragMoved.current = true;
    const size = Math.max(event.currentTarget.getBoundingClientRect().width, 1);
    setViewport((current) => ({
      ...current,
      centerX: Math.round(start.centerX + ((start.x - event.clientX) / size) * current.span),
      centerY: Math.round(start.centerY + ((start.y - event.clientY) / size) * current.span),
    }));
  };

  const onPointerEnd = () => { dragStart.current = null; };

  const onWheel = (event: React.WheelEvent<SVGSVGElement>) => {
    event.preventDefault();
    zoom(event.deltaY > 0 ? 1 : -1);
  };

  const minX = viewport.centerX - Math.floor(viewport.span / 2);
  const minY = viewport.centerY - Math.floor(viewport.span / 2);

  if (loading) return <div className="labyrinth-page"><div className="loading">{t('common.loading')}</div></div>;

  return (
    <section className="labyrinth-page">
      <div className="labyrinth-shell">
        <div className="labyrinth-top-tabs">
          <span className="labyrinth-top-tab is-active">✦ {t('labyrinth.title')}</span>
          <span className="labyrinth-top-tab">{t('labyrinth.communityMap')}</span>
        </div>
        <header className="labyrinth-heading">
          <div>
            <div className="labyrinth-kicker">{t('labyrinth.communityMap')}</div>
            <h1>{t('labyrinth.title')}</h1>
            <p>{t('labyrinth.description')}</p>
          </div>
          <button type="button" className="labyrinth-refresh" onClick={() => void loadSummary()}>↻ {t('common.refresh')}</button>
        </header>

        {error && <div className="error-message">{error}</div>}

        <div className="labyrinth-summary">
          <div><strong>{summary?.total_rooms ?? 0}</strong><span>{t('labyrinth.observedRooms')}</span></div>
          <div><strong>{rooms.length}</strong><span>{t('labyrinth.visibleRooms')}</span></div>
          <div><strong>{summary?.updated_at ? new Intl.DateTimeFormat(i18n.language, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(summary.updated_at)) : '—'}</strong><span>{t('labyrinth.lastUpdate')}</span></div>
        </div>

        <div className="labyrinth-layout">
          <div className="labyrinth-arena">
            <div className="labyrinth-arena-glow" />
            <div className="labyrinth-map-wrap">
              {mapLoading && <div className="labyrinth-map-loading">{t('common.loading')}</div>}
              <svg className="labyrinth-map" viewBox={`${minX} ${minY} ${viewport.span} ${viewport.span}`} role="img" aria-label={t('labyrinth.mapLabel')} onPointerDown={onPointerDown} onPointerMove={onPointerMove} onPointerUp={onPointerEnd} onPointerCancel={onPointerEnd} onWheel={onWheel}>
                <defs>
                  <filter id="labyrinth-glow"><feGaussianBlur stdDeviation="0.11" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
                </defs>
                {rooms.map((room) => (
                  <g className={`labyrinth-room${selectedRoom?.x === room.x && selectedRoom?.y === room.y ? ' is-selected' : ''}`} key={`${room.x}:${room.y}`} onClick={() => {
                    if (dragMoved.current) {
                      dragMoved.current = false;
                      return;
                    }
                    setSelectedRoom(room);
                  }}>
                    <title>{`${t('labyrinth.coordinates', { x: room.x, y: room.y })}\n${room.event ?? t('labyrinth.unknown')}${room.emission_event ? `\n${t('labyrinth.emission')}: ${room.emission_event}` : ''}`}</title>
                    <rect x={room.x + 0.07} y={room.y + 0.07} width="0.86" height="0.86" rx="0.19" fill={eventColor(room.event)} />
                    <text x={room.x + 0.5} y={room.y + 0.61} textAnchor="middle">{eventIcon(room.event)}</text>
                    {room.emission_event && <circle className="labyrinth-emission-marker" cx={room.x + 0.78} cy={room.y + 0.22} r="0.12" filter="url(#labyrinth-glow)" />}
                  </g>
                ))}
              </svg>
            </div>
          </div>

          <aside className="labyrinth-side">
            <div className="labyrinth-event-card">
              <div className="labyrinth-event-label">{t('labyrinth.selectedRoom')}</div>
              {selectedRoom ? <>
                <div className="labyrinth-room-title">{t('labyrinth.coordinates', { x: selectedRoom.x, y: selectedRoom.y })}</div>
                <div className="labyrinth-event-title"><span style={{ color: eventColor(selectedRoom.event) }}>{eventIcon(selectedRoom.event)}</span> {selectedRoom.event ?? t('labyrinth.unknown')}</div>
                <div className="labyrinth-event-text">{t('labyrinth.sources', { count: selectedRoom.sources_count })}</div>
                {selectedRoom.emission_event && <div className="labyrinth-emission-card">⚡ <strong>{t('labyrinth.emission')}</strong><br />{selectedRoom.emission_event}</div>}
              </> : <div className="labyrinth-event-text">{t('labyrinth.selectRoom')}</div>}
            </div>

            <div className="labyrinth-controls" aria-label={t('labyrinth.navigationLabel')}>
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
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
};

export default LabyrinthMapPage;
