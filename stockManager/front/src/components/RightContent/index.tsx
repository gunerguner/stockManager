import { Tag, Space } from 'antd';
import React, { useMemo } from 'react';
import { useModel } from 'umi';
import Avatar from './AvatarDropdown';
import styles from './index.less';

export type SiderTheme = 'light' | 'dark';

// 环境标签颜色配置
const ENV_TAG_COLORS = {
  dev: 'orange',
  test: 'green',
  pre: '#87d068',
} as const;

/**
 * 页面右侧内容组件
 * 显示用户头像下拉菜单和环境标签
 */
const RightContent: React.FC = () => {
  const { initialState } = useModel('@@initialState');

  // 计算样式类名
  const className = useMemo(() => {
    if (!initialState?.settings) {
      return styles.right;
    }

    const { navTheme, layout } = initialState.settings;
    const isDarkMode = (navTheme === 'dark' && layout === 'top') || layout === 'mix';

    return isDarkMode ? `${styles.right} ${styles.dark}` : styles.right;
  }, [initialState?.settings]);

  // 如果初始状态或设置不存在，返回 null
  if (!initialState || !initialState.settings) {
    return null;
  }

  return (
    <Space className={className}>
      <Avatar />
      {REACT_APP_ENV && REACT_APP_ENV in ENV_TAG_COLORS && (
        <Tag color={ENV_TAG_COLORS[REACT_APP_ENV as keyof typeof ENV_TAG_COLORS]}>
          {REACT_APP_ENV}
        </Tag>
      )}
    </Space>
  );
};

export default RightContent;
