import { useState, useEffect } from 'react';

/** 检测是否为移动端（屏幕宽度 ≤ 768px） */
export const useIsMobile = (): boolean => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    const handler = () => setIsMobile(mediaQuery.matches);

    handler();
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return isMobile;
};
