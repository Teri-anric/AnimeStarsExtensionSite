import { CardApi } from '../client';
import { createAuthenticatedClient } from './apiClient';

/** Card was removed at the source; drop our copy. */
export async function reportRemovedCard(cardId: number): Promise<void> {
  const cardApi = createAuthenticatedClient(CardApi);
  await cardApi.reportDeletedCardApiCardCardIdReportDeletedCardPost(cardId);
}
