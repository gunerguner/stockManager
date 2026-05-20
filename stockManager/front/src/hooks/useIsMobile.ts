import { useState, useEffect } from 'react';
import { SCREEN_MD_MAX } from '@/utils/constants';

/** 检测是否为移动端（屏幕宽度 ≤ SCREEN_MD_MAX） */
export const useIsMobile = (): boolean => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(`(max-width: ${SCREEN_MD_MAX}px)`);
    const handler = () => setIsMobile(mediaQuery.matches);

    handler();
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return isMobile;
};
