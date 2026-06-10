/**
 * 交易时间工具函数（A 股 / 港股）
 */

import { isHoliday } from 'chinese-days';

export type MarketId = 'cn' | 'hk';

export type TradingTimeStatus = {
  market: MarketId;
  isTrading: boolean;
  message: string;
};

const MARKET_LABEL: Record<MarketId, string> = {
  cn: 'A股',
  hk: '港股',
};

const MARKET_PERIODS: Record<MarketId, readonly { start: number; end: number }[]> = {
  cn: [
    { start: 9 * 60 + 30, end: 11 * 60 + 30 },
    { start: 13 * 60, end: 15 * 60 },
  ],
  hk: [
    { start: 9 * 60 + 30, end: 12 * 60 },
    { start: 13 * 60, end: 16 * 60 },
  ],
};

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

  const currentMinutes = currentTime.getHours() * 60 + currentTime.getMinutes();
  const isTodayTradingDay = isTradingDay(currentTime);
  const isTrading =
    isTodayTradingDay &&
    periods.some(({ start, end }) => currentMinutes >= start && currentMinutes < end);

  if (isTrading) {
    const closeMinutes = currentMinutes < morningClose ? morningClose : afternoonClose;
    const minutesToClose = closeMinutes - currentMinutes;
    return {
      market,
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

  const minutesToOpen = Math.ceil(
    (createDateWithMinutes(openDate, openMinutes).getTime() - currentTime.getTime()) / 60000,
  );
  return {
    market,
    isTrading: false,
    message: `${MARKET_LABEL[market]} 距开盘 ${formatMinutes(minutesToOpen)}`,
  };
};

export const getAllTradingTimeStatuses = (currentTime = new Date()): TradingTimeStatus[] =>
  (['cn', 'hk'] as MarketId[]).map((m) => getStatusForMarket(m, currentTime));
