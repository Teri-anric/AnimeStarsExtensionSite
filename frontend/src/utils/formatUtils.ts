/**
 * Formats a number with locale-specific formatting
 * @param value - Number to format
 * @param options - Optional Intl.NumberFormatOptions
 * @returns Localized number string
 */
export const formatNumber = (
  value: number | null | undefined,
  options?: Intl.NumberFormatOptions
): string | undefined => {
  if (value === null || value === undefined) return undefined;
  return value.toLocaleString(undefined, options);
};

