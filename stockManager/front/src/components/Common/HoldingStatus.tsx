import React from 'react';
import { CheckCircleTwoTone } from '@ant-design/icons';
import { theme, Tooltip, Typography } from 'antd';
import { useModel } from '@umijs/max';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { isHkCode, toXueqiuStockUrl } from '@/utils/format/stock';
import './index.less';

const { Link } = Typography;

const STOCK_NAME_CELL_STYLE: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 5,
};

const HOLDING_ICON_STYLE: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
};

const HoldingIcon: React.FC<{
  isProfit: boolean;
  profitColor: string;
  lossColor: string;
  isDark: boolean;
}> = ({ isProfit, profitColor, lossColor, isDark }) => {
  const { token } = theme.useToken();
  const primary = isProfit ? profitColor : lossColor;
  const secondary = isProfit
    ? token.colorErrorBg
    : // 白天模式下让绿色框填充稍微淡一点；暗夜模式保持 antd 默认值不变
      isDark
      ? token.colorSuccessBg
      : `color-mix(in srgb, ${token.colorSuccessBg} 40%, white)`;

  return (
    <CheckCircleTwoTone twoToneColor={[primary, secondary]} style={{ fontSize: '0.8em' }} />
  );
};

export type HoldingStatusProps = {
  name: string;
  code: string;
  holdCount?: number;
  holding?: boolean;
  offsetTotal?: number;
  netIncome?: number;
  isProfit?: boolean;
  withLink?: boolean;
  nameClassName?: string;
};

/** 股票名称单元格：港股/持仓标识，可选跳转雪球 */
export const HoldingStatus: React.FC<HoldingStatusProps> = ({
  name,
  code,
  holdCount,
  holding: holdingOverride,
  offsetTotal,
  netIncome,
  isProfit: isProfitOverride,
  withLink,
  nameClassName,
}) => {
  const { profitColor, lossColor } = useProfitLossColors();
  const { actualTheme } = useModel('theme');
  const isDark = actualTheme === 'dark';
  const isProfit = isProfitOverride ?? (netIncome ?? offsetTotal ?? 0) > 0;
  const holding = holdingOverride ?? (holdCount ?? 0) > 0;
  const isHk = isHkCode(code);
  const link = withLink ? toXueqiuStockUrl(code) : undefined;

  const nameNode = link ? (
    <Link href={link} target="_blank" rel="noreferrer" strong className="stock-group-link">
      {name}
    </Link>
  ) : (
    <span className={nameClassName}>{name}</span>
  );

  const content = (
    <span style={STOCK_NAME_CELL_STYLE}>
      {nameNode}
      {(isHk || holding) && (
        <span style={HOLDING_ICON_STYLE}>
          {isHk && <span aria-label="港股">🇭🇰</span>}
          {holding && (
            <HoldingIcon
              isProfit={isProfit}
              profitColor={profitColor}
              lossColor={lossColor}
              isDark={isDark}
            />
          )}
        </span>
      )}
    </span>
  );

  return <Tooltip title={code}>{content}</Tooltip>;
};
