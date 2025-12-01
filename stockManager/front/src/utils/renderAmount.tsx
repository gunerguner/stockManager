/**
 * 金额渲染工具函数
 */

import React from 'react';
import { colorFromValue } from './index';

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

