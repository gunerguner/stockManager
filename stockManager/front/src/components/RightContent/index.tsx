import { Tag, Space } from 'antd';
import { useMemo } from 'react';
import { useModel } from '@umijs/max';
import Avatar from './AvatarDropdown';
import ThemeSwitch from './ThemeSwitch';
import TradingTime from './TradingTime';
import { getEnv } from '@/utils';
import { ENV_TAG_COLORS } from '@/utils/constants';
import { useIsMobile } from '@/hooks/useIsMobile';
import styles from './index.less';

// ==================== 组件 ====================

const RightContent: React.FC = () => {
  const { initialState } = useModel('@@initialState');
  const isMobile = useIsMobile();

  const className = useMemo(() => {
    if (!initialState?.settings) return styles.right;

    const { navTheme, layout } = initialState.settings;
    const isDarkMode = navTheme === 'realDark' && (layout === 'top' || layout === 'mix');
    return isDarkMode ? `${styles.right} ${styles.dark}` : styles.right;
  }, [initialState?.settings]);

  if (!initialState?.settings) return null;

  const env = getEnv();

  return (
    <Space className={className} size={isMobile ? 4 : 0} align="center" wrap={isMobile}>
      <TradingTime />
      <ThemeSwitch />
      <Avatar />
      {!isMobile && env && env in ENV_TAG_COLORS && (
        <Tag color={ENV_TAG_COLORS[env as keyof typeof ENV_TAG_COLORS]}>{env}</Tag>
      )}
    </Space>
  );
};

export default RightContent;
