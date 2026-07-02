import { Tag, Space } from 'antd';
import { useModel } from '@umijs/max';
import Avatar from './AvatarDropdown';
import ThemeSwitch from './ThemeSwitch';
import TradingTime from './TradingTime';
import { ENV_TAG_COLORS, getEnv } from '@/utils/browser';
import { useIsMobile } from '@/hooks/useIsMobile';
import styles from './index.less';

const RightContent: React.FC = () => {
  const { initialState } = useModel('@@initialState');
  const isMobile = useIsMobile();

  if (!initialState?.settings) return null;

  const env = getEnv();

  return (
    <Space className={styles.right} size={isMobile ? 4 : 0} align="center" wrap={isMobile}>
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
