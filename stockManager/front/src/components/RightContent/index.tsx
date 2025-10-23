import { Tag, Space } from 'antd';
import React, { useMemo } from 'react';
import { useModel } from '@umijs/max';
import Avatar from './AvatarDropdown';
import styles from './index.less';


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

  // 计算样式类名 - 根据 navTheme 判断是否使用暗色样式
  const className = useMemo(() => {
    if (!initialState?.settings) {
      return styles.right;
    }

    const { navTheme, layout } = initialState.settings;
    // 当 navTheme 是 dark 或 realDark 且布局是 top 时，或布局是 mix 且 navTheme 不是 light 时，使用暗色样式
    const isDarkMode = 
      ( navTheme === 'realDark') && 
      (layout === 'top' || layout === 'mix');

    return isDarkMode ? `${styles.right} ${styles.dark}` : styles.right;
  }, [initialState?.settings]);

  // 如果初始状态或设置不存在，返回 null
  if (!initialState || !initialState.settings) {
    return null;
  }

  const env = process.env.REACT_APP_ENV;
  
  return (
    <Space className={className}>
      <Avatar />
      {env && env in ENV_TAG_COLORS && (
        <Tag color={ENV_TAG_COLORS[env as keyof typeof ENV_TAG_COLORS]}>
          {env}
        </Tag>
      )}
    </Space>
  );
};

export default RightContent;
