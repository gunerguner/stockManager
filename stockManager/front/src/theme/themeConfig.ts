import type { ThemeConfig } from 'antd';
import { theme } from 'antd';

/** 与 variables.less 保持一致 */
export const PRIMARY_COLOR = '#1677ff';

/** A 股下跌色，略深于 antd 默认 success 绿 */
export const STOCK_LOSS_COLOR = '#389e0d';
export const STOCK_LOSS_COLOR_DARK = '#3c8618';

const sharedToken = {
  colorPrimary: PRIMARY_COLOR,
  colorSuccess: STOCK_LOSS_COLOR,
  borderRadius: 8,
  colorBgLayout: '#f5f7fa',
  colorBgContainer: '#ffffff',
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
  fontSizeHeading3: 20,
  boxShadowSecondary:
    '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02)',
};

const sharedComponents: ThemeConfig['components'] = {
  Layout: {
    headerHeight: 56,
    headerBg: '#ffffff',
    bodyBg: '#f5f7fa',
  },
  Menu: {
    itemSelectedColor: PRIMARY_COLOR,
    horizontalItemSelectedColor: PRIMARY_COLOR,
  },
  Table: {
    headerBg: '#fafafa',
    headerColor: 'rgba(0, 0, 0, 0.88)',
    rowHoverBg: '#f5f7fa',
    borderColor: '#f0f0f0',
    cellPaddingBlock: 12,
    cellPaddingInline: 12,
  },
  Card: {
    paddingLG: 20,
  },
  Statistic: {
    titleFontSize: 13,
    contentFontSize: 28,
  },
  Tabs: {
    inkBarColor: PRIMARY_COLOR,
    itemSelectedColor: PRIMARY_COLOR,
    itemHoverColor: PRIMARY_COLOR,
  },
};

export const lightThemeConfig: ThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    ...sharedToken,
    colorText: 'rgba(0, 0, 0, 0.88)',
    colorTextSecondary: 'rgba(0, 0, 0, 0.65)',
  },
  components: sharedComponents,
};

export const darkThemeConfig: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    ...sharedToken,
    colorBgLayout: '#141414',
    colorBgContainer: '#1f1f1f',
    colorSuccess: STOCK_LOSS_COLOR_DARK,
    colorText: 'rgba(255, 255, 255, 0.85)',
    colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
  },
  components: {
    ...sharedComponents,
    Layout: {
      headerHeight: 56,
      headerBg: '#1f1f1f',
      bodyBg: '#141414',
    },
    Table: {
      headerBg: '#262626',
      headerColor: 'rgba(255, 255, 255, 0.85)',
      rowHoverBg: '#262626',
      borderColor: '#303030',
      cellPaddingBlock: 12,
      cellPaddingInline: 12,
    },
  },
};

export type ActualTheme = 'light' | 'dark';

export function getThemeConfig(actualTheme: ActualTheme): ThemeConfig {
  return actualTheme === 'dark' ? darkThemeConfig : lightThemeConfig;
}

/** antd 6.3+ 默认关闭 mask blur，此处恢复 antd 6.0~6.2 的模糊遮罩 */
const maskBlur = { blur: true } as const;

/** ConfigProvider 组件级配置（非 theme token，与主题一并维护） */
export const providerComponentConfig = {
  modal: { mask: maskBlur },
  drawer: { mask: maskBlur },
};
