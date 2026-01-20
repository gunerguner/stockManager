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
  const isTodayTradingDay = isTradingDay(currentTime);
  const isTrading = isTodayTradingDay && isTradingTime(currentTime);

  if (isTrading) {
    const closeMinutes = currentMinutes < MORNING_CLOSE ? MORNING_CLOSE : AFTERNOON_CLOSE;
    const closeTime = createDateWithMinutes(currentTime, closeMinutes);
    return {
      isTrading: true,
      message: `距收盘 ${formatMinutes(diffMinutes(closeTime, currentTime))}`,
    };
  }

  let openMinutes: number;
  let openDate: Date;

  if (isTodayTradingDay && currentMinutes < MORNING_OPEN) {
    openMinutes = MORNING_OPEN;
    openDate = currentTime;
  } else if (isTodayTradingDay && currentMinutes >= MORNING_CLOSE && currentMinutes < AFTERNOON_OPEN) {
    openMinutes = AFTERNOON_OPEN;
    openDate = currentTime;
  } else {
    openMinutes = MORNING_OPEN;
    openDate = createDateWithMinutes(currentTime, 0, 1);
    while (!isTradingDay(openDate)) {
      openDate.setDate(openDate.getDate() + 1);
    }
  }

  const openTime = createDateWithMinutes(openDate, openMinutes);
  return {
    isTrading: false,
    message: `距开盘 ${formatMinutes(diffMinutes(openTime, currentTime))}`,
  };
};

