export interface AdminDatabaseStats {
  total_cards: number;
  total_users: number;
  cards_with_stats: number;
  cards_stats_today: number;
}

export interface AdminExtensionBanner {
  title: string;
  message: string;
  action_text: string | null;
  action_url: string | null;
  is_active: boolean;
}

export interface BannerFormState {
  title: string;
  message: string;
  action_text: string;
  action_url: string;
  is_active: boolean;
}
