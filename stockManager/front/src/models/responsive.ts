import { useState, useEffect } from 'react';
import { SCREEN_MD_MAX } from '@/utils/layoutConstants';

const getIsMobile = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia(`(max-width: ${SCREEN_MD_MAX}px)`).matches;
};

export default () => {
  const [isMobile, setIsMobile] = useState(getIsMobile);

  useEffect(() => {
    const mediaQuery = window.matchMedia(`(max-width: ${SCREEN_MD_MAX}px)`);
    const handler = () => setIsMobile(mediaQuery.matches);

    handler();
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return { isMobile };
};
