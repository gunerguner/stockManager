import React from 'react';
import { CheckCircleTwoTone } from '@ant-design/icons';
import { Tooltip, Typography } from 'antd';
import { colorFromValue, formatMarketAmount } from './stock';

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

// ==================== 金额渲染 ====================
export const renderAmount = (
  value: number,
  color?: string,
  precision: number = 2,
  code?: string,
): React.ReactNode => {
  const displayColor = color || colorFromValue(value);
  return (
    <span style={{ color: displayColor }}>{formatMarketAmount(value, code, precision)}</span>
  );
};

// ==================== 股票名称与持有状态 ====================

export type RenderHoldingStatusParams = {
  name: string;
  code: string;
  link?: string;
  isProfit: boolean;
  holding: boolean;
  isHk: boolean;
  nameClassName?: string;
};

/** 渲染股票名称及持有状态，业务判断由调用方完成 */
export const renderHoldingStatus = ({
  name,
  code,
  link,
  isProfit,
  holding,
  isHk,
  nameClassName,
}: RenderHoldingStatusParams): React.ReactNode => {
  const iconColor = isProfit ? 'red' : '#33b317f1';

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
            <CheckCircleTwoTone twoToneColor={iconColor} style={{ fontSize: '0.8em' }} />
          )}
        </span>
      )}
    </span>
  );

  return <Tooltip title={code}>{content}</Tooltip>;
};
