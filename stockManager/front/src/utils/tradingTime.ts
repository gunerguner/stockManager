/**
 * 交易时间工具函数
 */

import { isHoliday } from 'chinese-days';

// ==================== 类型定义 ====================

export type TradingTimeStatus = {
  isTrading: boolean;
  message: string;
};

// ==================== 配置 ====================

/** 交易时间关键节点（分钟数） */
const MORNING_OPEN = 9 * 60 + 30;   // 9:30 上午开盘
const MORNING_CLOSE = 11 * 60 + 30; // 11:30 上午收盘
const AFTERNOON_OPEN = 13 * 60;     // 13:00 下午开盘
const AFTERNOON_CLOSE = 15 * 60;    // 15:00 下午收盘

/** 交易时间段 */
const TRADING_PERIODS = [
  { start: MORNING_OPEN, end: MORNING_CLOSE },
  { start: AFTERNOON_OPEN, end: AFTERNOON_CLOSE },
] as const;

// ==================== 内部工具函数 ====================

const toMinutes = (date: Date) => date.getHours() * 60 + date.getMinutes();

const createDateWithMinutes = (baseDate: Date, minutes: number, dayOffset = 0): Date => {
  const date = new Date(baseDate);
  if (dayOffset) date.setDate(date.getDate() + dayOffset);
  date.setHours(Math.floor(minutes / 60), minutes % 60, 0, 0);
  return date;
};

const isTradingDay = (date: Date) => {
  const day = date.getDay();
  return day !== 0 && day !== 6 && !isHoliday(date);
};

const isTradingTime = (date: Date) => {
  const minutes = toMinutes(date);
  return TRADING_PERIODS.some(({ start, end }) => minutes >= start && minutes < end);
};

const diffMinutes = (date1: Date, date2: Date) =>
  Math.ceil((date1.getTime() - date2.getTime()) / 60000);

const formatMinutes = (minutes: number): string => {
  if (minutes < 60) return `${minutes} 分钟`;

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours < 24) {
    return mins > 0 ? `${hours} 小时 ${mins} 分钟` : `${hours} 小时`;
  }

  const days = Math.floor(hours / 24);
  const hrs = hours % 24;
  const parts = [days > 0 && `${days} 天`, hrs > 0 && `${hrs} 小时`, mins > 0 && `${mins} 分钟`];
  return parts.filter(Boolean).join(' ');
};

// ==================== 导出函数 ====================

export const getTradingTimeStatus = (currentTime = new Date()): TradingTimeStatus => {
  const currentMinutes = toMinutes(currentTime);
  const isDay = isTradingDay(currentTime);
  // 只有在交易日且处于交易时间段内，才算交易中
  const isTrading = isDay && isTradingTime(currentTime);

  if (isTrading) {
    const closeMinutes = currentMinutes < MORNING_CLOSE ? MORNING_CLOSE : AFTERNOON_CLOSE;
    const closeTime = createDateWithMinutes(currentTime, closeMinutes);
    return {
      isTrading: true,
      message: `距收盘 ${formatMinutes(diffMinutes(closeTime, currentTime))}`,
    };
  }

  // 中午休市时间（必须是交易日）
  if (isDay && currentMinutes >= MORNING_CLOSE && currentMinutes < AFTERNOON_OPEN) {
    const openTime = createDateWithMinutes(currentTime, AFTERNOON_OPEN);
    return {
      isTrading: false,
      message: `距开盘 ${formatMinutes(diffMinutes(openTime, currentTime))}`,
    };
  }

  // 查找下一个交易日
  let checkDate = createDateWithMinutes(currentTime, 0, 1);
  for (let i = 0; i < 10; i++) {
    if (isTradingDay(checkDate)) {
      const openTime = createDateWithMinutes(checkDate, MORNING_OPEN);
      return {
        isTrading: false,
        message: `距开盘 ${formatMinutes(diffMinutes(openTime, currentTime))}`,
      };
    }
    checkDate.setDate(checkDate.getDate() + 1);
  }

  return { isTrading: false, message: '赌场关门了' };
};

