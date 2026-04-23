import React from 'react';
import { CheckCircleTwoTone } from '@ant-design/icons';

// ==================== 颜色工具 ====================
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

// ==================== 价格格式化 ====================
export const formatPrice = (value?: number | string | null): string => {
  if (value === undefined || value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const fixed3 = numValue.toFixed(3);
  return fixed3.endsWith('0') ? numValue.toFixed(2) : fixed3;
};

// ==================== 金额渲染 ====================
export const renderAmount = (
  value: number,
  color?: string,
  precision: number = 2,
): React.ReactNode => {
  const displayColor = color || colorFromValue(value);
  return <span style={{ color: displayColor }}>{value.toFixed(precision)}</span>;
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
