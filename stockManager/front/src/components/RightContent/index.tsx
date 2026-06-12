import { Tag, Space } from 'antd';
import { useMemo } from 'react';
import { useModel } from '@umijs/max';
import Avatar from './AvatarDropdown';
import ThemeSwitch from './ThemeSwitch';
import TradingTime from './TradingTime';
import { ENV_TAG_COLORS, getEnv } from '@/utils/browser';
import { useIsMobile } from '@/hooks/useIsMobile';
import styles from './index.less';

const RightContent: React.FC = () => {
  const { actualTheme } = useModel('theme');
  const { initialState } = useModel('@@initialState');
  const isMobile = useIsMobile();

  const className = useMemo(() => {
    const isDarkMode = actualTheme === 'dark';
    return isDarkMode ? `${styles.right} ${styles.dark}` : styles.right;
  }, [actualTheme]);

  if (!initialState?.settings) return null;

  const env = getEnv();

  return (
    <Space className={className} size={isMobile ? 4 : 0} align="center" wrap={isMobile}>
      {!isMobile && <TradingTime />}
      <ThemeSwitch />
      <Avatar />
      {!isMobile && env && env in ENV_TAG_COLORS && (
        <Tag color={ENV_TAG_COLORS[env as keyof typeof ENV_TAG_COLORS]}>{env}</Tag>
      )}
    </Space>
  );
};

export default RightContent;
