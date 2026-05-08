import { useCallback, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import type { AdminExtensionBanner, BannerFormState } from '../types';

interface UseAdminBannerResult {
  bannerLoading: boolean;
  bannerSaving: boolean;
  bannerError: string | null;
  bannerSuccess: string | null;
  bannerForm: BannerFormState;
  setBannerForm: Dispatch<SetStateAction<BannerFormState>>;
  fetchBannerConfig: () => Promise<void>;
  saveBannerConfig: () => Promise<void>;
}

export const useAdminBanner = (t: (key: string) => string): UseAdminBannerResult => {
  const [bannerLoading, setBannerLoading] = useState<boolean>(false);
  const [bannerSaving, setBannerSaving] = useState<boolean>(false);
  const [bannerError, setBannerError] = useState<string | null>(null);
  const [bannerSuccess, setBannerSuccess] = useState<string | null>(null);
  const [bannerForm, setBannerForm] = useState<BannerFormState>({
    title: '',
    message: '',
    action_text: '',
    action_url: '',
    is_active: false,
  });

  const fetchBannerConfig = useCallback(async () => {
    try {
      setBannerLoading(true);
      setBannerError(null);
      setBannerSuccess(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/extension-banner`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 403) {
        setBannerError(t('settings.adminAccessDenied'));
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch extension banner config');
      }

      const data: AdminExtensionBanner = await response.json();
      setBannerForm({
        title: data.title,
        message: data.message,
        action_text: data.action_text ?? '',
        action_url: data.action_url ?? '',
        is_active: data.is_active,
      });
    } catch (err) {
      console.error('Failed to fetch extension banner config:', err);
      setBannerError(t('settings.failedToLoadBannerConfig'));
    } finally {
      setBannerLoading(false);
    }
  }, [t]);

  const saveBannerConfig = useCallback(async () => {
    try {
      setBannerSaving(true);
      setBannerError(null);
      setBannerSuccess(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token');
      }

      const actionText = bannerForm.action_text.trim();
      const actionUrl = bannerForm.action_url.trim();
      if (actionText && !actionUrl) {
        setBannerError(t('settings.bannerActionUrlRequired'));
        return;
      }

      const payload = {
        title: bannerForm.title.trim(),
        message: bannerForm.message.trim(),
        action_text: actionText || null,
        action_url: actionUrl || null,
        is_active: bannerForm.is_active,
      };

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/extension-banner`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 403) {
        setBannerError(t('settings.adminAccessDenied'));
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to save extension banner config');
      }

      const data: AdminExtensionBanner = await response.json();
      setBannerForm({
        title: data.title,
        message: data.message,
        action_text: data.action_text ?? '',
        action_url: data.action_url ?? '',
        is_active: data.is_active,
      });
      setBannerSuccess(t('settings.bannerSaved'));
    } catch (err) {
      console.error('Failed to save extension banner config:', err);
      setBannerError(t('settings.failedToSaveBannerConfig'));
    } finally {
      setBannerSaving(false);
    }
  }, [bannerForm, t]);

  return {
    bannerLoading,
    bannerSaving,
    bannerError,
    bannerSuccess,
    bannerForm,
    setBannerForm,
    fetchBannerConfig,
    saveBannerConfig,
  };
};
