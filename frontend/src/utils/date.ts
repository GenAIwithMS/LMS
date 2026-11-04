// Today's date as "2026-11-04", in the user's own time zone
// (toISOString would give the UTC date, which can be yesterday early in the morning).
export const todayText = (): string => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};
