import React from 'react';
import { CheckCircleTwoTone } from '@ant-design/icons';
import { colorFromValue, formatAmount } from './stock';

// ==================== 金额渲染 ====================
export const renderAmount = (
  value: number,
  color?: string,
  precision: number = 2,
): React.ReactNode => {
  const displayColor = color || colorFromValue(value);
  return <span style={{ color: displayColor }}>{formatAmount(value, precision)}</span>;
};

// ==================== 持有状态图标 ====================
/**
 * 渲染持有状态 CheckCircleTwoTone 图标
 * @param holding 是否持有中
 * @param profit 盈亏值（正数红色，负数绿色）
 */
export const renderHoldingStatus = (holding: boolean, profit: number): React.ReactNode => {
  if (!holding) return null;
  const iconColor = profit > 0 ? 'red' : '#33b317f1';
  return <CheckCircleTwoTone twoToneColor={iconColor} style={{ fontSize: '0.8em' }} />;
};
