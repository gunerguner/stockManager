/**
 * 工具函数集合
 * 包含颜色、环境变量、CSRF Token、交易时间等通用工具函数
 */

import { isHoliday } from 'chinese-days';

// ==================== 颜色工具 ====================

/**
 * 根据数值返回对应的颜色
 * @param value - 数值
 * @returns 颜色字符串：正数返回 'red'，负数返回 'green'，零返回空字符串
 */
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

/**
 * 格式化价格：最少2位小数，最多3位小数
 * @param value - 价格值（数字或字符串）
 * @returns 格式化后的价格字符串
 */
export const formatPrice = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return String(value);
  
  // 四舍五入到3位小数
  const rounded = Math.round(numValue * 1000) / 1000;
  const str = rounded.toString();
  const decimalIndex = str.indexOf('.');
  
  // 没有小数部分或小数位数少于2位，补0到2位
  if (decimalIndex === -1 || str.substring(decimalIndex + 1).length < 2) {
    return rounded.toFixed(2);
  }
  
  // 小数位数在2-3位之间，保持原样
  return str;
};

// ==================== 环境变量工具 ====================

/**
 * 环境类型
 */
export type EnvType = 'dev' | 'test' | 'pre' | 'prod';

/**
 * 获取当前环境变量
 * 使用 Umi 内置的 UMI_ENV 变量
 * @returns 环境类型，生产构建且未设置时返回 undefined
 */
export const getEnv = (): EnvType | undefined => {
  // @ts-ignore - UMI_ENV 是 Umi 自动注入的
  const umiEnv = process.env.UMI_ENV;
  // @ts-ignore - NODE_ENV 是 webpack 自动注入的
  const nodeEnv = process.env.NODE_ENV;

  // 优先使用 UMI_ENV
  if (umiEnv) {
    return umiEnv as EnvType;
  }

  // 开发环境默认为 'dev'
  if (nodeEnv === 'development') {
    return 'dev';
  }

  // 生产构建且未设置 UMI_ENV，返回 undefined（不显示环境标签）
  return undefined;
};

// ==================== CSRF Token 工具 ====================

/**
 * 从 Cookie 中获取 CSRF Token
 * @returns CSRF Token 或 null
 */
export const getCsrfToken = (): string | null => {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');

  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith(`${name}=`)) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }

  return null;
};

// ==================== 交易时间工具 ====================

/**
 * 交易时间关键节点（分钟数）
 */
const MORNING_OPEN_MINUTES = 9 * 60 + 30; // 9:30 上午开盘
const MORNING_CLOSE_MINUTES = 11 * 60 + 30; // 11:30 上午收盘
const AFTERNOON_OPEN_MINUTES = 13 * 60; // 13:00 下午开盘
const AFTERNOON_CLOSE_MINUTES = 15 * 60; // 15:00 下午收盘

/**
 * 交易时间段配置（分钟数）
 */
const TRADING_PERIODS = [
  { start: MORNING_OPEN_MINUTES, end: MORNING_CLOSE_MINUTES }, // 上午：9:30 - 11:30
  { start: AFTERNOON_OPEN_MINUTES, end: AFTERNOON_CLOSE_MINUTES }, // 下午：13:00 - 15:00
] as const;

/**
 * 交易时间关键节点（从 TRADING_PERIODS 中提取，保持向后兼容）
 */
const MORNING_END_MINUTES = TRADING_PERIODS[0].end; // 11:30
const AFTERNOON_START_MINUTES = TRADING_PERIODS[1].start; // 13:00

/**
 * 将时间转换为分钟数
 */
const _toMinutes = (date: Date): number => date.getHours() * 60 + date.getMinutes();

/**
 * 将分钟数转换为小时和分钟
 */
const _minutesToHoursMinutes = (minutes: number): [number, number] => {
  return [Math.floor(minutes / 60), minutes % 60];
};

/**
 * 基于基准日期创建新的 Date 对象，并设置指定的时间（分钟数）
 * @param baseDate - 基准日期
 * @param minutes - 时间（分钟数）
 * @param dayOffset - 日期偏移量（可选，默认为 0）
 */
const _createDateWithMinutes = (baseDate: Date, minutes: number, dayOffset: number = 0): Date => {
  const date = new Date(baseDate);
  if (dayOffset !== 0) {
    date.setDate(date.getDate() + dayOffset);
  }
  const [hour, minute] = _minutesToHoursMinutes(minutes);
  date.setHours(hour, minute, 0, 0);
  return date;
};

/**
 * 判断指定日期是否是交易日
 */
const _isTradingDay = (date: Date): boolean => {
  const dayOfWeek = date.getDay();
  return dayOfWeek !== 0 && dayOfWeek !== 6 && !isHoliday(date);
};

/**
 * 判断指定时间是否在交易时间段内
 */
const _isTradingTime = (time: Date): boolean => {
  const minutes = _toMinutes(time);
  return TRADING_PERIODS.some(({ start, end }) => minutes >= start && minutes < end);
};

/**
 * 计算两个日期之间的分钟差
 */
const _diffMinutes = (date1: Date, date2: Date): number => {
  return Math.ceil((date1.getTime() - date2.getTime()) / (1000 * 60));
};

/**
 * 将分钟数转换为可读的时间格式（x天y小时z分钟）
 */
const _formatMinutes = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} 分钟`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (hours < 24) {
    return remainingMinutes > 0 ? `${hours} 小时 ${remainingMinutes} 分钟` : `${hours} 小时`;
  }
  
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  
  const parts: string[] = [];
  if (days > 0) {
    parts.push(`${days} 天`);
  }
  if (remainingHours > 0) {
    parts.push(`${remainingHours} 小时`);
  }
  if (remainingMinutes > 0) {
    parts.push(`${remainingMinutes} 分钟`);
  }
  
  return parts.join(' ');
};

/**
 * 交易时间状态类型
 */
export type TradingTimeStatus = {
  isTrading: boolean;
  message: string;
};

/**
 * 获取交易时间状态
 */
export const getTradingTimeStatus = (currentTime: Date = new Date()): TradingTimeStatus => {
  const currentMinutes = _toMinutes(currentTime);
  const isTrading = _isTradingTime(currentTime);

  if (isTrading) {
    // 交易时间内，计算距离最近一个收盘时间
    // 上午（9:30-11:30）：距离 11:30 收盘
    // 下午（13:00-15:00）：距离 15:00 收盘
    const closeTime = currentMinutes < MORNING_END_MINUTES
      ? _createDateWithMinutes(currentTime, MORNING_CLOSE_MINUTES)
      : _createDateWithMinutes(currentTime, AFTERNOON_CLOSE_MINUTES);
    
    const minutesToClose = _diffMinutes(closeTime, currentTime);
    return {
      isTrading: true,
      message: `距收盘 ${_formatMinutes(minutesToClose)}`,
    };
  }

  // 不在交易时间内，计算距离下一个开盘时间
  // 如果是交易日且在中午休市时间（11:30-13:00），返回当天下午开盘时间
  if (_isTradingDay(currentTime) && currentMinutes >= MORNING_END_MINUTES && currentMinutes < AFTERNOON_START_MINUTES) {
    const nextOpenTime = _createDateWithMinutes(currentTime, AFTERNOON_OPEN_MINUTES);
    const minutesToOpen = _diffMinutes(nextOpenTime, currentTime);
    return {
      isTrading: false,
      message: `距开盘 ${_formatMinutes(minutesToOpen)}`,
    };
  }

  // 查找下一个交易日的开盘时间（9:30）
  let checkDate = _createDateWithMinutes(currentTime, 0, 1);

  for (let i = 0; i < 10; i++) {
    if (_isTradingDay(checkDate)) {
      const openTime = _createDateWithMinutes(checkDate, MORNING_OPEN_MINUTES);
      const minutesToOpen = _diffMinutes(openTime, currentTime);
      return {
        isTrading: false,
        message: `距开盘 ${_formatMinutes(minutesToOpen)}`,
      };
    }
    checkDate.setDate(checkDate.getDate() + 1);
  }

  // 10天内找不到交易日，返回"赌场关门了"
  return {
    isTrading: false,
    message: '赌场关门了',
  };
};