// Where the login is kept in the browser, and how we notice the user left.
//
// The login is kept in sessionStorage, not localStorage:
// - sessionStorage survives a page refresh,
// - but the browser deletes it when the tab or the browser is closed,
//   so closing the LMS logs the user out straight away.
// Each tab has its own sessionStorage, so a new tab needs its own login.

const TOKEN_KEY = 'token';
const USER_KEY = 'user';
const LEFT_KEY = 'lms_left_page';

export const getSavedLogin = (): string | null => {
  return sessionStorage.getItem(TOKEN_KEY);
};

export const saveLogin = (token: string, user: object | null) => {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const clearSavedLogin = () => {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
  // Logins from before this change were kept in localStorage; remove those too
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

// Called when the page goes away: the tab is closed, another site is opened
// in this tab, or the page is refreshed.
export const markPageLeft = () => {
  sessionStorage.setItem(LEFT_KEY, 'yes');
};

// True if the user left the LMS (for example to another website) and came back
// with the Back button. A page refresh does not count as leaving.
export const userCameBackAfterLeaving = (): boolean => {
  const leftBefore = sessionStorage.getItem(LEFT_KEY) === 'yes';
  sessionStorage.removeItem(LEFT_KEY);
  if (!leftBefore) {
    return false;
  }

  const entries = performance.getEntriesByType('navigation');
  const navigation = entries[0] as PerformanceNavigationTiming | undefined;
  const wasRefresh = navigation !== undefined && navigation.type === 'reload';
  return !wasRefresh;
};
