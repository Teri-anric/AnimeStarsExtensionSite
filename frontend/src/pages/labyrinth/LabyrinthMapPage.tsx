import { useCallback, useEffect, useRef, useState, type FormEvent, type KeyboardEvent, type PointerEvent, type WheelEvent } from 'react';
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

type OverviewCell = { x: number; y: number; room_count: number };
type LabyrinthRoomHistoryItem = { event: string; is_emission: boolean; created_at: string };
type Viewport = { centerX: number; centerY: number; span: number };

const DETAIL_SPAN = 32;
const MIN_SPAN = 12;
const MAX_SPAN = 200001;
const basePath = import.meta.env.VITE_API_URL ?? '';
const apiUrl = (path: string) => `${basePath}${path}`;

const eventColor = (event: string | null): string => {
  if (!event || event === 'unknown') return '#59616d';
  if (event.includes('boss')) return '#c24f64';
  if (event.includes('trap')) return '#b65a7e';
  if (event.includes('mine') || event.includes('gift') || event.includes('chest')) return '#b7873f';
  if (event.includes('recovery') || event.includes('luck')) return '#4e9a79';
  if (event.includes('relic') || event.includes('resonance')) return '#8067bc';
  if (event.includes('trader')) return '#4c8db8';
  let hash = 0;
  for (const character of event) hash = (hash * 31 + character.charCodeAt(0)) | 0;
  return `hsl(${Math.abs(hash) % 360} 48% 52%)`;
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
  const width = summary.max_x - summary.min_x + 1;
  const height = summary.max_y - summary.min_y + 1;
  return {
    centerX: Math.floor((summary.min_x + summary.max_x) / 2),
    centerY: Math.floor((summary.min_y + summary.max_y) / 2),
    span: Math.max(24, Math.min(MAX_SPAN, Math.ceil(Math.max(width, height) * 1.12))),
  };
};

const parseCoordinates = (input: string): { x: number; y: number } | null => {
  const match = input.match(/^\s*(?:x\s*[:=]\s*)?(-?\d+)\s*(?:,|;)\s*(?:y\s*[:=]\s*)?(-?\d+)\s*$/i);
  if (!match) return null;
  const x = Number(match[1]);
  const y = Number(match[2]);
  if (!Number.isSafeInteger(x) || !Number.isSafeInteger(y) || Math.abs(x) > 100000 || Math.abs(y) > 100000) return null;
  return { x, y };
};

const LabyrinthMapPage = () => {
  const { t, i18n } = useTranslation();
  const [summary, setSummary] = useState<LabyrinthSummary | null>(null);
  const summaryRef = useRef<LabyrinthSummary | null>(null);
  const initialized = useRef(false);
  const [viewport, setViewport] = useState<Viewport>({ centerX: 0, centerY: 0, span: 48 });
  const [rooms, setRooms] = useState<LabyrinthRoom[]>([]);
  const [overviewCells, setOverviewCells] = useState<OverviewCell[]>([]);
  const [overviewBucket, setOverviewBucket] = useState(1);
  const [selectedRoom, setSelectedRoom] = useState<LabyrinthRoom | null>(null);
  const [focusCoordinates, setFocusCoordinates] = useState<{ x: number; y: number } | null>(null);
  const [history, setHistory] = useState<LabyrinthRoomHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [mapLoading, setMapLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LabyrinthRoom[]>([]);
  const [searchHasMore, setSearchHasMore] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [searchError, setSearchError] = useState(false);
  const dragStart = useRef<{ x: number; y: number; centerX: number; centerY: number } | null>(null);
  const dragMoved = useRef(false);
  const activePointers = useRef(new Map<number, { x: number; y: number }>());
  const pinchStart = useRef<{ distance: number; span: number } | null>(null);
  const suppressClick = useRef(false);

  const loadSummary = useCallback(async () => {
    if (summaryRef.current) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const response = await axios.get<LabyrinthSummary>(apiUrl('/api/extension/labyrinth/map/summary'));
      if (!response.data || !Number.isFinite(response.data.total_rooms)) throw new Error('Invalid labyrinth summary');
      summaryRef.current = response.data;
      setSummary(response.data);
      if (!initialized.current) {
        setViewport(initialViewport(response.data));
        initialized.current = true;
      }
    } catch {
      setError(t('labyrinth.loadError'));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [t]);

  useEffect(() => { void loadSummary(); }, [loadSummary]);

  useEffect(() => {
    if (!summary) return;
    const controller = new AbortController();
    const minX = viewport.centerX - Math.floor(viewport.span / 2);
    const minY = viewport.centerY - Math.floor(viewport.span / 2);
    const clampCoordinate = (value: number) => Math.max(-100000, Math.min(100000, value));
    const queryMinX = clampCoordinate(minX);
    const queryMaxX = clampCoordinate(minX + viewport.span - 1);
    const queryMinY = clampCoordinate(minY);
    const queryMaxY = clampCoordinate(minY + viewport.span - 1);
    const requestTimer = window.setTimeout(() => {
      setMapLoading(true);
      if (viewport.span > DETAIL_SPAN) {
      const bucketSize = Math.max(1, Math.ceil(viewport.span / 32));
      setOverviewBucket(bucketSize);
      axios.get<{ cells: OverviewCell[] }>(apiUrl('/api/extension/labyrinth/map/overview'), {
        params: {
          bucket_size: bucketSize,
          min_x: queryMinX,
          max_x: queryMaxX,
          min_y: queryMinY,
          max_y: queryMaxY,
        },
        signal: controller.signal,
      }).then((response) => {
        if (!Array.isArray(response.data.cells)) throw new Error('Invalid labyrinth overview');
        setOverviewCells(response.data.cells);
        setRooms([]);
        setError(null);
      }).catch((requestError) => {
        if (!axios.isCancel(requestError)) setError(t('labyrinth.loadError'));
      }).finally(() => {
        if (!controller.signal.aborted) setMapLoading(false);
      });
      } else {
      axios.get<{ rooms: LabyrinthRoom[] }>(apiUrl('/api/extension/labyrinth/map'), {
        params: {
          min_x: queryMinX,
          max_x: queryMaxX,
          min_y: queryMinY,
          max_y: queryMaxY,
        },
        signal: controller.signal,
      }).then((response) => {
        if (!Array.isArray(response.data.rooms)) throw new Error('Invalid labyrinth map');
        setRooms(response.data.rooms);
        setOverviewCells([]);
        setSelectedRoom((current) => current
          ? response.data.rooms.find((room) => room.x === current.x && room.y === current.y) ?? current
          : null);
        setError(null);
      }).catch((requestError) => {
        if (!axios.isCancel(requestError)) setError(t('labyrinth.loadError'));
      }).finally(() => {
        if (!controller.signal.aborted) setMapLoading(false);
      });
      }
    }, 90);
    return () => {
      window.clearTimeout(requestTimer);
      controller.abort();
    };
  }, [summary, t, viewport]);

  useEffect(() => {
    if (!focusCoordinates || viewport.span > DETAIL_SPAN) return;
    const match = rooms.find((room) => room.x === focusCoordinates.x && room.y === focusCoordinates.y);
    if (match) setSelectedRoom(match);
  }, [focusCoordinates, rooms, viewport.span]);

  useEffect(() => {
    if (!selectedRoom) {
      setHistory([]);
      return;
    }
    const controller = new AbortController();
    setHistoryLoading(true);
    axios.get<{ history: LabyrinthRoomHistoryItem[] }>(
      apiUrl(`/api/extension/labyrinth/rooms/${selectedRoom.x}/${selectedRoom.y}/history`),
      { signal: controller.signal },
    ).then((response) => setHistory(Array.isArray(response.data.history) ? response.data.history : []))
      .catch((requestError) => { if (!axios.isCancel(requestError)) setHistory([]); })
      .finally(() => { if (!controller.signal.aborted) setHistoryLoading(false); });
    return () => controller.abort();
  }, [selectedRoom]);

  const zoom = (direction: 1 | -1) => {
    setViewport((current) => ({
      ...current,
      span: Math.max(MIN_SPAN, Math.min(MAX_SPAN, Math.round(current.span * (direction > 0 ? 1.7 : 0.58)))),
    }));
  };

  const onPointerDown = (event: PointerEvent<SVGSVGElement>) => {
    activePointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (activePointers.current.size === 1) {
      dragStart.current = { x: event.clientX, y: event.clientY, centerX: viewport.centerX, centerY: viewport.centerY };
      dragMoved.current = false;
    } else {
      const [first, second] = [...activePointers.current.values()];
      pinchStart.current = { distance: Math.hypot(first.x - second.x, first.y - second.y), span: viewport.span };
      dragStart.current = null;
    }
    const target = event.target instanceof Element ? event.target : null;
    if (!target?.closest('.labyrinth-room, .labyrinth-cluster')) {
      event.currentTarget.setPointerCapture(event.pointerId);
    }
  };

  const onPointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (activePointers.current.has(event.pointerId)) {
      activePointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    }
    if (activePointers.current.size >= 2 && pinchStart.current) {
      const [first, second] = [...activePointers.current.values()];
      const distance = Math.max(1, Math.hypot(first.x - second.x, first.y - second.y));
      setViewport((current) => ({
        ...current,
        span: Math.max(MIN_SPAN, Math.min(MAX_SPAN, Math.round(pinchStart.current!.span * pinchStart.current!.distance / distance))),
      }));
      dragMoved.current = true;
      return;
    }
    const start = dragStart.current;
    if (!start) return;
    if (Math.abs(start.x - event.clientX) > 4 || Math.abs(start.y - event.clientY) > 4) dragMoved.current = true;
    const size = Math.max(event.currentTarget.getBoundingClientRect().width, 1);
    setViewport((current) => ({
      ...current,
      centerX: Math.round(start.centerX + ((start.x - event.clientX) / size) * current.span),
      centerY: Math.round(start.centerY + ((start.y - event.clientY) / size) * current.span),
    }));
  };

  const onPointerEnd = (event: PointerEvent<SVGSVGElement>) => {
    activePointers.current.delete(event.pointerId);
    if (activePointers.current.size === 1) {
      const remaining = [...activePointers.current.values()][0];
      dragStart.current = { ...remaining, centerX: viewport.centerX, centerY: viewport.centerY };
      pinchStart.current = null;
      return;
    }
    dragStart.current = null;
    pinchStart.current = null;
    if (dragMoved.current) {
      suppressClick.current = true;
      window.setTimeout(() => { suppressClick.current = false; }, 120);
    }
  };

  const consumeSuppressedClick = () => {
    if (!suppressClick.current) return false;
    suppressClick.current = false;
    return true;
  };

  const onWheel = (event: WheelEvent<SVGSVGElement>) => {
    event.preventDefault();
    zoom(event.deltaY > 0 ? 1 : -1);
  };

  const focusRoom = (room: LabyrinthRoom) => {
    setQuery('');
    setSearchResults([]);
    setSearchHasMore(false);
    setSearchPerformed(false);
    setFocusCoordinates({ x: room.x, y: room.y });
    setSelectedRoom(room);
    setViewport({ centerX: room.x, centerY: room.y, span: 24 });
  };

  const searchByEventType = async (term: string, append = false) => {
    if (!term) return;
    setSearchPerformed(true);
    setSearchError(false);
    if (!append) {
      setSearchResults([]);
      setSearchHasMore(false);
    }
    setSearchLoading(true);
    try {
      const response = await axios.get<{ rooms: LabyrinthRoom[]; has_more: boolean }>(apiUrl('/api/extension/labyrinth/map/search'), {
        params: { q: term, limit: 50, offset: append ? searchResults.length : 0 },
      });
      if (!Array.isArray(response.data.rooms)) throw new Error('Invalid labyrinth search result');
      setSearchResults((current) => append ? [...current, ...response.data.rooms] : response.data.rooms);
      setSearchHasMore(response.data.has_more === true);
    } catch {
      setSearchError(true);
    } finally {
      setSearchLoading(false);
    }
  };

  const onSearch = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    const coordinates = parseCoordinates(trimmed);
    setSearchPerformed(true);
    setSearchError(false);
    setSearchResults([]);
    setSearchHasMore(false);
    if (coordinates) {
      setFocusCoordinates(coordinates);
      setSelectedRoom(null);
      setViewport({ centerX: coordinates.x, centerY: coordinates.y, span: 24 });
      return;
    }
    await searchByEventType(trimmed);
  };

  const fitToMap = () => {
    if (!summary) return;
    setFocusCoordinates(null);
    setViewport(initialViewport(summary));
  };

  const selectMapRoom = (room: LabyrinthRoom) => {
    if (consumeSuppressedClick()) return;
    setFocusCoordinates({ x: room.x, y: room.y });
    setSelectedRoom(room);
  };

  const selectCluster = (cell: OverviewCell) => {
    if (consumeSuppressedClick()) return;
    const nextSpan = viewport.span < DETAIL_SPAN * 3
      ? DETAIL_SPAN
      : Math.max(DETAIL_SPAN + 1, Math.ceil(viewport.span / 3));
    setFocusCoordinates(null);
    setViewport({
      centerX: cell.x + Math.floor(overviewBucket / 2),
      centerY: cell.y + Math.floor(overviewBucket / 2),
      span: Math.min(viewport.span, nextSpan),
    });
  };

  const onRoomKeyDown = (event: KeyboardEvent<SVGGElement>, room: LabyrinthRoom) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectMapRoom(room);
    }
  };

  const minX = viewport.centerX - Math.floor(viewport.span / 2);
  const minY = viewport.centerY - Math.floor(viewport.span / 2);
  const isOverview = viewport.span > DETAIL_SPAN;
  const dateFormat = new Intl.DateTimeFormat(i18n.language, { dateStyle: 'medium', timeStyle: 'short' });

  if (loading) return <div className="labyrinth-page"><div className="loading">{t('common.loading')}</div></div>;

  return (
    <section className="labyrinth-page">
      <header className="labyrinth-heading">
        <div className="labyrinth-heading-copy">
          <span className="labyrinth-kicker">{t('labyrinth.communityMap')}</span>
          <h1>{t('labyrinth.title')}</h1>
          <p>{t('labyrinth.description')}</p>
        </div>
        <div className="labyrinth-header-meta">
          <div className="labyrinth-updated">
            <strong>{summary ? summary.total_rooms.toLocaleString(i18n.language) : '—'}</strong>
            <span>{t('labyrinth.observedRooms')}</span>
            <small>{summary?.updated_at ? t('labyrinth.lastUpdateValue', { date: dateFormat.format(new Date(summary.updated_at)) }) : t('labyrinth.noUpdate')}</small>
          </div>
          <button type="button" className="labyrinth-refresh" onClick={() => void loadSummary()} disabled={refreshing}>
            <span aria-hidden="true">↻</span> {refreshing ? t('common.loading') : t('common.refresh')}
          </button>
        </div>
      </header>

      <form className="labyrinth-search" onSubmit={onSearch} role="search">
        <label className="labyrinth-search-label" htmlFor="labyrinth-search-input">{t('labyrinth.searchLabel')}</label>
        <div className="labyrinth-search-row">
          <span className="labyrinth-search-icon" aria-hidden="true">⌕</span>
          <input
            id="labyrinth-search-input"
            type="search"
            value={query}
            onChange={(event) => { setQuery(event.target.value); setSearchPerformed(false); setSearchError(false); setSearchHasMore(false); setSearchResults([]); }}
            placeholder={t('labyrinth.searchPlaceholder')}
            aria-describedby="labyrinth-search-hint"
            aria-controls="labyrinth-search-results"
          />
          <button type="submit" className="labyrinth-search-submit" disabled={!query.trim() || searchLoading}>
            {searchLoading ? t('common.loading') : t('labyrinth.searchAction')}
          </button>
        </div>
        <span id="labyrinth-search-hint" className="labyrinth-search-hint">{t('labyrinth.searchHint')}</span>
        {(searchLoading || searchError || searchPerformed && query.trim() && !parseCoordinates(query) || searchResults.length > 0) && (
          <div id="labyrinth-search-results" className="labyrinth-search-results" role="region" aria-label={t('labyrinth.searchLabel')} aria-live="polite">
            {searchLoading ? <p>{t('common.loading')}</p> : searchError ? <div className="labyrinth-search-error"><p>{t('labyrinth.searchError')}</p><button type="button" onClick={() => void searchByEventType(query.trim(), searchResults.length > 0)}>{t('labyrinth.searchRetry')}</button></div> : searchResults.length ? <>
              {searchResults.map((room) => (
                <button type="button" key={`${room.x}:${room.y}`} onClick={() => focusRoom(room)}>
                  <span className="search-result-icon" style={{ color: eventColor(room.event) }} aria-hidden="true">{eventIcon(room.event)}</span>
                  <span><strong>{room.event ?? t('labyrinth.unknown')}</strong><small>{t('labyrinth.coordinates', { x: room.x, y: room.y })}{room.emission_event ? ` · ${t('labyrinth.emission')}` : ''}</small></span>
                </button>
              ))}
              {searchHasMore && <button type="button" className="labyrinth-search-more" onClick={() => void searchByEventType(query.trim(), true)}>{t('labyrinth.searchLoadMore')}</button>}
            </> : searchPerformed && query.trim() && !parseCoordinates(query) ? <p>{t('labyrinth.noSearchResults')}</p> : null}
          </div>
        )}
      </form>

      {error && <div className="labyrinth-error" role="alert"><span>{error}</span><button type="button" onClick={() => void loadSummary()}>{t('common.refresh')}</button></div>}

      <section className="labyrinth-workspace" aria-label={t('labyrinth.mapLabel')}>
        <div className="labyrinth-map-column">
          <div className="labyrinth-map-toolbar">
            <div className="labyrinth-map-context">
              <span className="labyrinth-live-dot" />
              <strong>{isOverview ? t('labyrinth.overviewMode') : t('labyrinth.detailMode')}</strong>
              <span>{isOverview ? t('labyrinth.clusterCount', { count: overviewCells.length }) : t('labyrinth.visibleRoomCount', { count: rooms.length })}</span>
            </div>
            <button type="button" className="labyrinth-fit-button" onClick={fitToMap}>⌗ <span>{t('labyrinth.fitMap')}</span></button>
          </div>
          <div className="labyrinth-arena">
            <div className="labyrinth-map-wrap">
              {mapLoading && <div className="labyrinth-map-loading" role="status">{t('common.loading')}</div>}
              <svg
                className="labyrinth-map"
                viewBox={`${minX} ${minY} ${viewport.span} ${viewport.span}`}
                role="group"
                aria-label={t('labyrinth.mapLabel')}
                onPointerDown={onPointerDown}
                onPointerMove={onPointerMove}
                onPointerUp={onPointerEnd}
                onPointerCancel={onPointerEnd}
                onWheel={onWheel}
              >
                <defs>
                  <pattern id="labyrinth-grid" width="1" height="1" patternUnits="userSpaceOnUse">
                    <path d="M 1 0 L 0 0 0 1" fill="none" stroke="rgba(255,255,255,.12)" strokeWidth="0.025" />
                  </pattern>
                </defs>
                <rect x={minX} y={minY} width={viewport.span} height={viewport.span} fill="url(#labyrinth-grid)" pointerEvents="none" />
                {isOverview ? overviewCells.map((cell) => (
                  <g
                    className="labyrinth-cluster"
                    key={`${cell.x}:${cell.y}`}
                    role="button"
                    tabIndex={0}
                    aria-label={t('labyrinth.clusterLabel', { count: cell.room_count, x: cell.x, y: cell.y })}
                    onClick={() => selectCluster(cell)}
                    onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectCluster(cell); } }}
                  >
                    <rect
                      x={cell.x + overviewBucket * 0.08}
                      y={cell.y + overviewBucket * 0.08}
                      width={overviewBucket * 0.84}
                      height={overviewBucket * 0.84}
                      rx={overviewBucket * 0.16}
                      style={{ fillOpacity: 0.22 + Math.min(0.7, Math.log2(cell.room_count + 1) * 0.12) }}
                    />
                    <title>{t('labyrinth.clusterLabel', { count: cell.room_count, x: cell.x, y: cell.y })}</title>
                    {overviewBucket / viewport.span > 0.03 && <text x={cell.x + overviewBucket / 2} y={cell.y + overviewBucket * 0.58} fontSize={overviewBucket * 0.5} textAnchor="middle">{cell.room_count}</text>}
                  </g>
                )) : rooms.map((room) => (
                  <g
                    className={`labyrinth-room${selectedRoom?.x === room.x && selectedRoom?.y === room.y ? ' is-selected' : ''}`}
                    key={`${room.x}:${room.y}`}
                    role="button"
                    tabIndex={0}
                    aria-label={`${t('labyrinth.coordinates', { x: room.x, y: room.y })}, ${room.event ?? t('labyrinth.unknown')}${room.emission_event ? `, ${t('labyrinth.emission')}: ${room.emission_event}` : ''}`}
                    onClick={() => selectMapRoom(room)}
                    onKeyDown={(event) => onRoomKeyDown(event, room)}
                  >
                    <title>{`${t('labyrinth.coordinates', { x: room.x, y: room.y })}\n${room.event ?? t('labyrinth.unknown')}${room.emission_event ? `\n${t('labyrinth.emission')}: ${room.emission_event}` : ''}`}</title>
                    <rect x={room.x + 0.08} y={room.y + 0.08} width="0.84" height="0.84" rx="0.2" fill={eventColor(room.event)} />
                    <text x={room.x + 0.5} y={room.y + 0.62} textAnchor="middle">{eventIcon(room.event)}</text>
                    {room.emission_event && <circle className="labyrinth-emission-marker" cx={room.x + 0.78} cy={room.y + 0.22} r="0.12" />}
                  </g>
                ))}
              </svg>
              {summary?.total_rooms === 0 && <div className="labyrinth-empty-map">{t('labyrinth.emptyMap')}</div>}
              {summary && summary.total_rooms > 0 && !mapLoading && (isOverview ? overviewCells.length === 0 : rooms.length === 0) && <div className="labyrinth-empty-map">{t('labyrinth.noRoomsInView')}</div>}
              <div className="labyrinth-map-controls" aria-label={t('labyrinth.navigationLabel')}>
                <button type="button" onClick={() => zoom(-1)} aria-label={t('labyrinth.zoomIn')}>+</button>
                <span aria-hidden="true" />
                <button type="button" onClick={() => zoom(1)} aria-label={t('labyrinth.zoomOut')}>−</button>
              </div>
              <div className="labyrinth-map-coordinates">X {viewport.centerX} <span>·</span> Y {viewport.centerY}</div>
            </div>
          </div>
          <div className="labyrinth-legend">
            <span><i className="legend-room" />{t('labyrinth.room')}</span>
            <span><i className="legend-emission" />{t('labyrinth.emission')}</span>
            {isOverview && <span><i className="legend-cluster" />{t('labyrinth.clusterLegend')}</span>}
          </div>
        </div>

        <aside className={`labyrinth-detail-panel${selectedRoom || focusCoordinates ? ' has-selection' : ''}`} aria-live="polite">
          <div className="labyrinth-detail-heading">
            <div><span className="labyrinth-kicker">{t('labyrinth.selectedRoom')}</span><h2>{selectedRoom ? selectedRoom.event ?? t('labyrinth.unknown') : t('labyrinth.roomDetails')}</h2></div>
            {selectedRoom && <span className="labyrinth-event-badge" style={{ color: eventColor(selectedRoom.event) }}>{eventIcon(selectedRoom.event)}</span>}
          </div>
          {selectedRoom ? <>
            <div className="labyrinth-room-coordinates">{t('labyrinth.coordinates', { x: selectedRoom.x, y: selectedRoom.y })}</div>
            <div className="labyrinth-room-observations"><span>{t('labyrinth.observationCount')}</span><strong>{selectedRoom.sources_count.toLocaleString(i18n.language)}</strong></div>
            {selectedRoom.emission_event && <div className="labyrinth-emission-card"><span aria-hidden="true">⚡</span><div><strong>{t('labyrinth.emission')}</strong><span>{selectedRoom.emission_event}</span></div></div>}
            <div className="labyrinth-history">
              <h3>{t('labyrinth.history')}</h3>
              {historyLoading ? <p>{t('common.loading')}</p> : history.length ? <ol>{history.map((item, index) => (
                <li key={`${item.created_at}:${item.event}:${index}`}>
                  <span className="history-icon" style={{ color: eventColor(item.event) }}>{item.is_emission ? '⚡' : eventIcon(item.event)}</span>
                  <span><strong>{item.event}{item.is_emission ? ` · ${t('labyrinth.emission')}` : ''}</strong><small>{dateFormat.format(new Date(item.created_at))}</small></span>
                </li>
              ))}</ol> : <p>{t('labyrinth.noHistory')}</p>}
            </div>
          </> : focusCoordinates ? <div className="labyrinth-coordinate-empty">
            <strong>{t('labyrinth.coordinates', focusCoordinates)}</strong>
            <p>{t('labyrinth.coordinateNotFound')}</p>
          </div> : <div className="labyrinth-detail-empty"><span aria-hidden="true">⌖</span><p>{t('labyrinth.selectRoom')}</p></div>}
        </aside>
      </section>
    </section>
  );
};

export default LabyrinthMapPage;
