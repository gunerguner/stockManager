import React from 'react';
import { CheckCircleTwoTone } from '@ant-design/icons';
import { theme, Tooltip, Typography } from 'antd';
import { colorFromValue, formatAmount, FormatAmountOptions } from './stock';

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

/** 持仓标识：主色 + 主题浅底，暗色模式随 token 适配 */
const HoldingIcon: React.FC<{
  isProfit: boolean;
  profitColor: string;
  lossColor: string;
}> = ({ isProfit, profitColor, lossColor }) => {
  const { token } = theme.useToken();
  const primary = isProfit ? profitColor : lossColor;
  const secondary = isProfit ? token.colorErrorBg : token.colorSuccessBg;

  return (
    <CheckCircleTwoTone twoToneColor={[primary, secondary]} style={{ fontSize: '0.8em' }} />
  );
};

export type ProfitLossColorOptions = {
  profitColor?: string;
  lossColor?: string;
};

export const renderAmount = (
  value: number,
  options?: FormatAmountOptions,
  color?: string,
  precision: number = 2,
  profitLossColors?: ProfitLossColorOptions,
): React.ReactNode => {
  const displayColor = color || colorFromValue(value, profitLossColors);
  return (
    <span style={{ color: displayColor }}>{formatAmount(value, options, precision)}</span>
  );
};

export type RenderHoldingStatusParams = {
  name: string;
  code: string;
  link?: string;
  isProfit: boolean;
  holding: boolean;
  isHk: boolean;
  nameClassName?: string;
  profitColor?: string;
  lossColor?: string;
};

export const renderHoldingStatus = ({
  name,
  code,
  link,
  isProfit,
  holding,
  isHk,
  nameClassName,
  profitColor = '#ff4d4f',
  lossColor = '#389e0d',
}: RenderHoldingStatusParams): React.ReactNode => {
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
            <HoldingIcon isProfit={isProfit} profitColor={profitColor} lossColor={lossColor} />
          )}
        </span>
      )}
    </span>
  );

  return <Tooltip title={code}>{content}</Tooltip>;
};
