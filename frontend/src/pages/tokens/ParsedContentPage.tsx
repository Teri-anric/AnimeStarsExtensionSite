import React, { useMemo } from 'react';
import PaginationPage, { PaginationQuery, PaginationResponse } from '../../components/PaginationPage';
import { EntityFilterConfig, GenericFilter } from '../../types/filter';
import authAxios from '../../utils/authAxios';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

interface ParsedContentItem {
  id: string;
  source: string;
  source_url?: string | null;
  content: string;
  created_at: string;
  tokens: string[];
}

const filterConfig: EntityFilterConfig = {
  entityName: 'Parsed Content',
  fieldOptions: [
    { value: 'source', label: 'Source', type: 'string' },
    { value: 'content', label: 'Content', type: 'string' },
    { value: 'created_at', label: 'Created At', type: 'datetime' },
  ],
  shortFilterFields: [
    { key: 'source', type: 'text', placeholder: 'Source' },
    { key: 'content', type: 'text', placeholder: 'Search content' },
  ],
  buildShortFilter: (values: Record<string, string>): GenericFilter | null => {
    const filters: GenericFilter[] = [];
    if (values.source) filters.push({ source: { icontains: values.source } });
    if (values.content) filters.push({ content: { icontains: values.content } });
    if (filters.length === 0) return null;
    if (filters.length === 1) return filters[0];
    return { and: filters };
  },
  sortOptions: [
    { value: 'created_at:desc', label: 'Newest' },
    { value: 'created_at:asc', label: 'Oldest' },
  ],
  defaults: {
    sort: 'created_at:desc',
    filterMode: 'short',
  },
  ui: {
    title: 'Parsed Content'
  }
};

const fetchParsedContent = async (query: PaginationQuery & { start_date?: string; end_date?: string }): Promise<PaginationResponse<ParsedContentItem>> => {
  const resp = await authAxios.post('/api/tokens/parsed-content', {
    page: query.page || 1,
    per_page: query.per_page || 20,
    filter: query.filter || undefined,
    order_by: query.order_by || undefined,
  }, {
    params: {
      start_date: query.start_date,
      end_date: query.end_date,
    }
  });
  return resp.data as PaginationResponse<ParsedContentItem>;
};

const ParsedContentPage: React.FC = () => {
  const { t } = useTranslation();
  const buildQuery = useMemo(() => {
    return (page: number, perPage: number, filter: GenericFilter | null, sortBy: string) => {
      const url = new URL(window.location.href);
      const start_date = url.searchParams.get('start_date') || undefined;
      const end_date = url.searchParams.get('end_date') || undefined;
      return {
        page,
        per_page: perPage,
        filter,
        order_by: sortBy,
        start_date,
        end_date,
      } as any;
    };
  }, []);

  return (
    <PaginationPage<ParsedContentItem, GenericFilter, any>
      title={t('parsedContent.title')}
      fetchData={fetchParsedContent as any}
      buildQuery={buildQuery}
      filterConfig={filterConfig}
      headerActions={(
        <div className="date-range-controls">
          <label>
            {t('parsedContent.from')}:
            <input type="datetime-local" defaultValue="" onChange={(e) => {
              const params = new URLSearchParams(window.location.search);
              if (e.target.value) params.set('start_date', new Date(e.target.value).toISOString()); else params.delete('start_date');
              window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
            }} />
          </label>
          <label>
            {t('parsedContent.to')}:
            <input type="datetime-local" defaultValue="" onChange={(e) => {
              const params = new URLSearchParams(window.location.search);
              if (e.target.value) params.set('end_date', new Date(e.target.value).toISOString()); else params.delete('end_date');
              window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
            }} />
          </label>
        </div>
      )}
      renderItems={(items) => (
        <div className="list">
          {items.map(item => (
            <div key={item.id} className="list-row">
              <div className="cell small">
                {item.source_url ? (
                  <a href={item.source_url} target="_blank" rel="noopener noreferrer">{item.source}</a>
                ) : (
                  item.source
                )}
              </div>
              <div className="cell grow">
                {item.content}
                {!!item.tokens?.length && (
                  <div className="tokens">
                    {item.tokens.map(tok => (
                      <Link key={tok} to={`/token/${encodeURIComponent(tok)}`} className="token-link">{tok}</Link>
                    ))}
                  </div>
                )}
              </div>
              <div className="cell small">{new Date(item.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      )}
    />
  );
};

export default ParsedContentPage;

