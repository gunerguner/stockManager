import { useModel } from '@umijs/max';

/** 检测是否为移动端（屏幕宽度 ≤ SCREEN_MD_MAX），共享单例监听 */
export const useIsMobile = (): boolean => {
  const { isMobile } = useModel('responsive');
  return isMobile;
};
