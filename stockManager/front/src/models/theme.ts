import { useState, useEffect, useCallback } from 'react';

// ==================== 类型定义 ====================

export type ActualTheme = 'light' | 'dark';
export type ThemeMode = ActualTheme | 'auto';

// ==================== 配置 ====================

const STORAGE_KEY = 'stock-manager-theme-mode';

// ==================== 工具函数 ====================

const getSystemTheme = (): ActualTheme =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';

const getSavedThemeMode = (): ThemeMode => {
  if (typeof window === 'undefined') return 'auto';
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved === 'light' || saved === 'dark' || saved === 'auto' ? saved : 'auto';
};

const getActualTheme = (mode: ThemeMode): ActualTheme =>
  mode === 'auto' ? getSystemTheme() : mode;

// ==================== Model ====================

export default function useThemeModel() {
  const [themeMode, setThemeModeState] = useState<ThemeMode>(getSavedThemeMode);
  const [actualTheme, setActualTheme] = useState<ActualTheme>(() => getActualTheme(getSavedThemeMode()));

  const setThemeMode = useCallback((mode: ThemeMode) => {
    setThemeModeState(mode);
    localStorage.setItem(STORAGE_KEY, mode);
    setActualTheme(getActualTheme(mode));
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      if (themeMode === 'auto') {
        setActualTheme(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [themeMode]);

  return { themeMode, actualTheme, setThemeMode };
}
