/**
 * Formats a date string into a human-readable "time ago" format
 * @param dateString - The date string to format (can be null/undefined)
 * @param options - Optional configuration for the formatting
 * @returns A human-readable string like "2h ago", "3d ago", etc.
 */
export const formatTimeAgo = (
  dateString: string | null | undefined,
): string | undefined => {
  if (!dateString) return undefined;
  if (!dateString.includes('Z')) dateString += 'Z';

  try {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMs = now.getTime() - date.getTime();

    if (diffInMs < 0) return 'Future date';

    const diffInSeconds = Math.floor(diffInMs / 1000);
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInWeeks = Math.floor(diffInDays / 7);
    const diffInMonths = Math.floor(diffInDays / 30);
    const diffInYears = Math.floor(diffInDays / 365);

    if (diffInSeconds <= 1) {
      return 'Just now';
    } else if (diffInSeconds < 60) {
      return `${diffInSeconds}s ago`;
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else if (diffInDays < 7) {
      return `${diffInDays}d ago`;
    } else if (diffInWeeks < 5) {
      return `${diffInWeeks}w ago`;
    } else if (diffInMonths < 12) {
      return `${diffInMonths}mo ago`;
    } else {
      return `${diffInYears}y ago`;
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