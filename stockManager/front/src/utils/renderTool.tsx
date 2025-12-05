/**
 * 金额 & 价格渲染工具
 */

import React from 'react';

// ==================== 颜色工具 ====================

/**
 * 根据数值返回对应的颜色
 */
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

// ==================== 价格格式化 ====================

/**
 * 格式化价格：如果第三位小数非 0 则保留 3 位，否则保留 2 位
 */
export const formatPrice = (value?: number | string | null): string => {
  if (value === undefined || value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const fixed3 = numValue.toFixed(3);
  return fixed3.endsWith('0') ? numValue.toFixed(2) : fixed3;
};

// ==================== 金额渲染 ====================

/**
 * 渲染金额
 * @param value 金额数值
 * @param color 颜色,不传则根据正负值自动判断
 * @param precision 小数位数,默认2位
 */
export const renderAmount = (
  value: number,
  color?: string,
  precision: number = 2,
): React.ReactNode => {
  const displayColor = color || colorFromValue(value);
  return <span style={{ color: displayColor }}>{value.toFixed(precision)}</span>;
};


