import React from 'react';
import PaginationPage, { PaginationQuery, PaginationResponse } from '../../components/PaginationPage';
import { EntityFilterConfig, GenericFilter } from '../../types/filter';
import authAxios from '../../utils/authAxios';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

interface IndexedToken {
  symbol: string;
  name?: string | null;
  mentions_24h: number;
  last_seen_at?: string | null;
}

const filterConfig: EntityFilterConfig = {
  entityName: 'Tokens',
  fieldOptions: [
    { value: 'symbol', label: 'Symbol', type: 'string' },
    { value: 'name', label: 'Name', type: 'string' },
  ],
  shortFilterFields: [
    { key: 'symbol', type: 'text', placeholder: 'Symbol' },
    { key: 'name', type: 'text', placeholder: 'Name' },
  ],
  buildShortFilter: (values: Record<string, string>): GenericFilter | null => {
    const filters: GenericFilter[] = [];
    if (values.symbol) filters.push({ symbol: { icontains: values.symbol } });
    if (values.name) filters.push({ name: { icontains: values.name } });
    if (filters.length === 0) return null;
    if (filters.length === 1) return filters[0];
    return { and: filters };
  },
  sortOptions: [
    { value: 'mentions_24h:desc', label: 'Mentions 24h (desc)' },
    { value: 'mentions_24h:asc', label: 'Mentions 24h (asc)' },
    { value: 'symbol:asc', label: 'Symbol (A-Z)' },
  ],
  defaults: {
    sort: 'mentions_24h:desc',
    filterMode: 'short',
  },
  ui: {
    title: 'Indexed Tokens'
  }
};

const fetchTokens = async (query: PaginationQuery): Promise<PaginationResponse<IndexedToken>> => {
  const resp = await authAxios.post('/api/tokens/list', {
    page: query.page || 1,
    per_page: query.per_page || 20,
    filter: query.filter || undefined,
    order_by: query.order_by || undefined,
  });
  return resp.data as PaginationResponse<IndexedToken>;
};

const IndexedTokensPage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  return (
    <PaginationPage<IndexedToken>
      title={t('tokensPage.title')}
      fetchData={fetchTokens}
      filterConfig={filterConfig}
      renderItems={(items) => (
        <div className="list">
          {items.map(item => (
            <div key={item.symbol} className="list-row clickable" onClick={() => navigate(`/token/${encodeURIComponent(item.symbol)}`)}>
              <div className="cell strong">{item.symbol}</div>
              <div className="cell">{item.name || '-'}</div>
              <div className="cell">{item.mentions_24h}</div>
              <div className="cell">{item.last_seen_at ? new Date(item.last_seen_at).toLocaleString() : '-'}</div>
            </div>
          ))}
        </div>
      )}
      headerActions={<Link to="/parsed-content">{t('tokensPage.viewParsedContent')}</Link>}
    />
  );
};

export default IndexedTokensPage;

