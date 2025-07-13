/**
 * Formats a date string into a human-readable "time ago" format
 * @param dateString - The date string to format (can be null/undefined)
 * @param t - Translation function (optional)
 * @returns A human-readable string like "2h ago", "3d ago", etc.
 */
export const formatTimeAgo = (
  dateString: string | null | undefined,
  t?: (key: string) => string
): string | undefined => {
  if (!dateString) return undefined;
  if (!dateString.includes('Z')) dateString += 'Z';

  try {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMs = now.getTime() - date.getTime();

    if (diffInMs < 0) return t ? t('dateTime.futureDate') : 'Future date';

    const diffInSeconds = Math.floor(diffInMs / 1000);
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInWeeks = Math.floor(diffInDays / 7);
    const diffInMonths = Math.floor(diffInDays / 30);
    const diffInYears = Math.floor(diffInDays / 365);

    if (diffInSeconds <= 1) {
      return t ? t('dateTime.justNow') : 'Just now';
    } else if (diffInSeconds < 60) {
      const suffix = t ? t('dateTime.secondsAgo') : 's ago';
      return `${diffInSeconds}${suffix}`;
    } else if (diffInMinutes < 60) {
      const suffix = t ? t('dateTime.minutesAgo') : 'm ago';
      return `${diffInMinutes}${suffix}`;
    } else if (diffInHours < 24) {
      const suffix = t ? t('dateTime.hoursAgo') : 'h ago';
      return `${diffInHours}${suffix}`;
    } else if (diffInDays < 7) {
      const suffix = t ? t('dateTime.daysAgo') : 'd ago';
      return `${diffInDays}${suffix}`;
    } else if (diffInWeeks < 5) {
      const suffix = t ? t('dateTime.weeksAgo') : 'w ago';
      return `${diffInWeeks}${suffix}`;
    } else if (diffInMonths < 12) {
      const suffix = t ? t('dateTime.monthsAgo') : 'mo ago';
      return `${diffInMonths}${suffix}`;
    } else {
      const suffix = t ? t('dateTime.yearsAgo') : 'y ago';
      return `${diffInYears}${suffix}`;
    }
  } catch {
    return undefined;
  }
};



function _createDate(dateString: string | number | Date): Date | undefined {
  if (!dateString) return undefined;
  if (typeof dateString === 'string' && !dateString.includes('Z')) dateString += 'Z';
  try {
    const date = new Date(dateString);
    return date;
  } catch {
    return undefined;
  }
}


/**
 * Formats a date string into a human-readable date format
 * @param dateString - The date string to format (can be null/undefined)
 * @returns A human-readable string like "12/31/2024, 12:00:00 AM"
 */
export const formatDateTime = (dateString: string | number | Date): string | undefined => {
  const date = _createDate(dateString);
  if (!date) return undefined;
  return date.toLocaleString();
};

/**
 * Formats a date or timestamp into a localized time string
 * @param date - Date object, timestamp, or date string
 * @param options - Optional Intl.DateTimeFormatOptions
 * @returns Localized time string
 */
export const formatTime = (
  date: Date | number | string,
  options?: Intl.DateTimeFormatOptions
): string | undefined => {
  const dateObj = _createDate(date);

  if (!dateObj) return undefined;
  return dateObj.toLocaleTimeString(undefined, options);
};


/**
 * Formats a date for chart tooltips with specific options
 * @param date - Date object, timestamp, or date string
 * @returns Formatted date string for charts
 */
export const formatChartDate = (date: Date | number | string): string | undefined => {
  const dateObj = _createDate(date);
  if (!dateObj) return undefined;
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Formats current time for status displays
 * @returns Current time as localized string
 */
export const formatCurrentTime = (): string | undefined => {
  return new Date().toLocaleTimeString();
};