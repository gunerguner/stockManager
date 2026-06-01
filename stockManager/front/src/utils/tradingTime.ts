/**
 * 交易时间工具函数（A 股 / 港股）
 */

import { isHoliday } from 'chinese-days';

// ==================== 类型定义 ====================

export type MarketId = 'cn' | 'hk';

export type TradingTimeStatus = {
  isTrading: boolean;
  message: string;
};

// ==================== 配置 ====================

const MARKET_LABEL: Record<MarketId, string> = {
  cn: 'A股',
  hk: '港股',
};

const CN_TRADING_PERIODS = [
  { start: 9 * 60 + 30, end: 11 * 60 + 30 },
  { start: 13 * 60, end: 15 * 60 },
] as const;

const HK_TRADING_PERIODS = [
  { start: 9 * 60 + 30, end: 12 * 60 },
  { start: 13 * 60, end: 16 * 60 },
] as const;

const MARKET_PERIODS: Record<MarketId, readonly { start: number; end: number }[]> = {
  cn: CN_TRADING_PERIODS,
  hk: HK_TRADING_PERIODS,
};

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

const isTradingTime = (date: Date, market: MarketId) => {
  const minutes = toMinutes(date);
  return MARKET_PERIODS[market].some(({ start, end }) => minutes >= start && minutes < end);
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

const getStatusForMarket = (market: MarketId, currentTime = new Date()): TradingTimeStatus => {
  const periods = MARKET_PERIODS[market];
  const morningOpen = periods[0].start;
  const morningClose = periods[0].end;
  const afternoonOpen = periods[1].start;
  const afternoonClose = periods[1].end;

  const currentMinutes = toMinutes(currentTime);
  const isTodayTradingDay = isTradingDay(currentTime);
  const isTrading = isTodayTradingDay && isTradingTime(currentTime, market);

  if (isTrading) {
    const closeMinutes = currentMinutes < morningClose ? morningClose : afternoonClose;
    const minutesToClose = closeMinutes - currentMinutes;
    return {
      isTrading: true,
      message: `${MARKET_LABEL[market]} 距收盘 ${formatMinutes(minutesToClose)}`,
    };
  }

  let openMinutes: number;
  let openDate: Date;

  if (isTodayTradingDay && currentMinutes < morningOpen) {
    openMinutes = morningOpen;
    openDate = currentTime;
  } else if (
    isTodayTradingDay &&
    currentMinutes >= morningClose &&
    currentMinutes < afternoonOpen
  ) {
    openMinutes = afternoonOpen;
    openDate = currentTime;
  } else {
    openMinutes = morningOpen;
    openDate = createDateWithMinutes(currentTime, 0, 1);
    while (!isTradingDay(openDate)) {
      openDate.setDate(openDate.getDate() + 1);
    }
  }

  const minutesToOpen = diffMinutes(createDateWithMinutes(openDate, openMinutes), currentTime);
  return {
    isTrading: false,
    message: `${MARKET_LABEL[market]} 距开盘 ${formatMinutes(minutesToOpen)}`,
  };
};

// ==================== 导出函数 ====================

export const getTradingTimeStatus = (
  market: MarketId = 'cn',
  currentTime = new Date(),
): TradingTimeStatus => getStatusForMarket(market, currentTime);

export const getAllTradingTimeStatuses = (currentTime = new Date()): TradingTimeStatus[] =>
  (['cn', 'hk'] as MarketId[]).map((m) => getTradingTimeStatus(m, currentTime));
