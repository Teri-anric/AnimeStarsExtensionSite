import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const TokenSentimentPage: React.FC = () => {
  const { symbol } = useParams();
  const { t } = useTranslation();
  return (
    <div className="token-sentiment-page">
      <div className="page-header">
        <h1>{t('tokenSentiment.title', { symbol })}</h1>
        <div className="actions">
          <Link to="/tokens" className="button">{t('tokenSentiment.viewAllTokens')}</Link>
        </div>
      </div>
      <div className="content">
        <p>Sentiment analysis coming soon.</p>
      </div>
    </div>
  );
};

export default TokenSentimentPage;

