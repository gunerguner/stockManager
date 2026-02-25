import React from 'react';

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
