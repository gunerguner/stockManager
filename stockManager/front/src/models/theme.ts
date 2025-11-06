import { useState, useEffect, useCallback } from 'react';

/**
 * 主题模式类型
 * - light: 白天模式
 * - dark: 暗夜模式
 * - auto: 跟随系统
 */
export type ThemeMode = 'light' | 'dark' | 'auto';

/**
 * 实际应用的主题类型（不包括 auto）
 */
export type ActualTheme = 'light' | 'dark';

const THEME_STORAGE_KEY = 'stock-manager-theme-mode';

/**
 * 获取系统主题偏好
 * @returns 系统当前的主题模式
 */
const getSystemTheme = (): ActualTheme => {
  if (typeof window === 'undefined') {
    return 'light';
  }
  
  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  return isDark ? 'dark' : 'light';
};

/**
 * 从本地存储获取保存的主题模式
 * @returns 保存的主题模式，如果没有则返回 'auto'
 */
const getSavedThemeMode = (): ThemeMode => {
  if (typeof window === 'undefined') {
    return 'auto';
  }
  
  const saved = localStorage.getItem(THEME_STORAGE_KEY);
  if (saved === 'light' || saved === 'dark' || saved === 'auto') {
    return saved;
  }
  
  return 'auto';
};

/**
 * 计算实际应用的主题
 * @param mode - 用户选择的主题模式
 * @returns 实际应用的主题
 */
const getActualTheme = (mode: ThemeMode): ActualTheme => {
  if (mode === 'auto') {
    return getSystemTheme();
  }
  return mode;
};

/**
 * 主题管理 Model
 * 提供主题模式的状态管理和切换功能
 * 配合 antd-style 的 ThemeProvider 使用
 */
export default function useThemeModel() {
  // 用户选择的主题模式
  const [themeMode, setThemeModeState] = useState<ThemeMode>(getSavedThemeMode);
  
  // 实际应用的主题（用于 antd-style）
  const [actualTheme, setActualTheme] = useState<ActualTheme>(() => 
    getActualTheme(getSavedThemeMode())
  );

  /**
   * 设置主题模式
   * @param mode - 要设置的主题模式
   */
  const setThemeMode = useCallback((mode: ThemeMode): void => {
    setThemeModeState(mode);
    localStorage.setItem(THEME_STORAGE_KEY, mode);
    
    const newActualTheme = getActualTheme(mode);
    setActualTheme(newActualTheme);
  }, []);

  /**
   * 监听系统主题变化
   * 仅在用户选择"跟随系统"时生效
   */
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemThemeChange = (e: MediaQueryListEvent): void => {
      if (themeMode === 'auto') {
        const newTheme = e.matches ? 'dark' : 'light';
        setActualTheme(newTheme);
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);

    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, [themeMode]);

  return {
    /** 用户选择的主题模式 */
    themeMode,
    /** 实际应用的主题（用于 antd-style 的 appearance） */
    actualTheme,
    /** 设置主题模式 */
    setThemeMode,
  };
}
