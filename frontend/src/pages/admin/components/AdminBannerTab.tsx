import { useTranslation } from 'react-i18next';
import type { Dispatch, SetStateAction } from 'react';
import type { BannerFormState } from '../types';

interface AdminBannerTabProps {
  bannerLoading: boolean;
  bannerSaving: boolean;
  bannerError: string | null;
  bannerSuccess: string | null;
  bannerForm: BannerFormState;
  setBannerForm: Dispatch<SetStateAction<BannerFormState>>;
  iframeUrl: string;
  iframeCode: string;
  onSave: () => Promise<void>;
  onRefresh: () => Promise<void>;
}

const AdminBannerTab = ({
  bannerLoading,
  bannerSaving,
  bannerError,
  bannerSuccess,
  bannerForm,
  setBannerForm,
  iframeUrl,
  iframeCode,
  onSave,
  onRefresh,
}: AdminBannerTabProps) => {
  const { t } = useTranslation();

  return (
    <div className="admin-section">
      <h3>{t('settings.extensionBanner')}</h3>
      <p className="admin-description">{t('settings.extensionBannerDescription')}</p>

      {(bannerError || bannerSuccess) && (
        <div className={bannerError ? 'admin-error-message' : 'admin-success-message'}>{bannerError || bannerSuccess}</div>
      )}

      {bannerLoading ? (
        <div className="admin-loading">{t('settings.loadingBannerConfig')}</div>
      ) : (
        <div className="admin-banner-layout">
          <div className="admin-banner-form">
            <div className="admin-field">
              <label htmlFor="banner-title">{t('settings.bannerTitle')}</label>
              <input
                id="banner-title"
                className="admin-input"
                value={bannerForm.title}
                onChange={(e) => setBannerForm((prev) => ({ ...prev, title: e.target.value }))}
                maxLength={120}
              />
            </div>
            <div className="admin-field">
              <label htmlFor="banner-message">{t('settings.bannerMessage')}</label>
              <textarea
                id="banner-message"
                className="admin-input"
                value={bannerForm.message}
                onChange={(e) => setBannerForm((prev) => ({ ...prev, message: e.target.value }))}
                maxLength={500}
                rows={4}
              />
            </div>
            <div className="admin-field">
              <label htmlFor="banner-action-text">{t('settings.bannerActionText')}</label>
              <input
                id="banner-action-text"
                className="admin-input"
                value={bannerForm.action_text}
                onChange={(e) => setBannerForm((prev) => ({ ...prev, action_text: e.target.value }))}
                maxLength={80}
              />
            </div>
            <div className="admin-field">
              <label htmlFor="banner-action-url">{t('settings.bannerActionUrl')}</label>
              <input
                id="banner-action-url"
                className="admin-input"
                value={bannerForm.action_url}
                onChange={(e) => setBannerForm((prev) => ({ ...prev, action_url: e.target.value }))}
                maxLength={512}
                placeholder="https://"
              />
            </div>
            <div className="admin-field admin-checkbox-row">
              <label htmlFor="banner-is-active">
                <input
                  id="banner-is-active"
                  type="checkbox"
                  checked={bannerForm.is_active}
                  onChange={(e) => setBannerForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                />
                {t('settings.bannerIsActive')}
              </label>
            </div>

            <div className="admin-field">
              <label htmlFor="banner-iframe-url">{t('settings.bannerIframeUrl')}</label>
              <input id="banner-iframe-url" className="admin-input" value={iframeUrl} readOnly />
            </div>
            <div className="admin-field">
              <label htmlFor="banner-iframe-code">{t('settings.bannerIframeCode')}</label>
              <textarea id="banner-iframe-code" className="admin-input" value={iframeCode} rows={3} readOnly />
            </div>

            <div className="admin-actions">
              <button onClick={onSave} className="button button-secondary" disabled={bannerSaving}>
                {bannerSaving ? t('common.loading') : t('common.save')}
              </button>
              <button onClick={onRefresh} className="button button-secondary" disabled={bannerLoading}>
                {t('common.refresh')}
              </button>
            </div>
          </div>

          <div className="admin-field admin-banner-preview-column">
            <h4>{t('settings.bannerLivePreview')}</h4>
            <div className="admin-banner-preview">
              <iframe
                src={iframeUrl}
                title="extension-banner-preview"
                style={{ width: '100%', minHeight: 110, border: 0 }}
                loading="lazy"
                referrerPolicy="no-referrer"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminBannerTab;
