import { useModel } from '@umijs/max';

/** 检测是否为移动端（屏幕宽度 ≤ SCREEN_MD_MAX），共享单例监听 */
export const useIsMobile = (): boolean => {
  const { isMobile } = useModel('responsive');
  return isMobile;
};

export const getResponsiveTableProps = (isMobile: boolean) => ({
  scroll: isMobile ? ({ x: 'max-content' } as const) : undefined,
  size: (isMobile ? 'small' : 'middle') as 'small' | 'middle',
  tableLayout: 'auto' as const,
});
