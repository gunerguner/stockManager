import { useState, useEffect } from 'react';

/**
 * 检测是否为移动端设备的 Hook
 * 使用媒体查询检测屏幕宽度是否小于 576px（Ant Design xs 断点）
 * 与 Ant Design 的响应式断点保持一致
 * 
 * @returns {boolean} 是否为移动端设备
 */
export const useIsMobile = (): boolean => {
  const [isMobile, setIsMobile] = useState<boolean>(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    
    const handleResize = (): void => {
      setIsMobile(mediaQuery.matches);
    };

    // 初始化
    handleResize();

    // 监听变化
    mediaQuery.addEventListener('change', handleResize);
    
    return () => {
      mediaQuery.removeEventListener('change', handleResize);
    };
  }, []);

  return isMobile;
};

