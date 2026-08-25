import { formatMarketPrice } from '@/utils/format/stock';

const inRange = (
  priceNow: number | null,
  point: number | null,
  cmp: (price: number, p: number) => boolean,
) => priceNow != null && point != null && point > 0 && cmp(priceNow, point);

export const isBuyPointTriggered = (priceNow: number | null, point: number | null): boolean =>
  inRange(priceNow, point, (price, p) => price <= p);

export const isBuyPointWarning = (priceNow: number | null, point: number | null): boolean =>
  inRange(priceNow, point, (price, p) => price > p && price <= p * 1.05);

export const isTrendPointTriggered = (priceNow: number | null, point: number | null): boolean =>
  inRange(priceNow, point, (price, p) => price >= p);

export const isTrendPointWarning = (priceNow: number | null, point: number | null): boolean =>
  inRange(priceNow, point, (price, p) => price < p && price >= p * 0.95);

export const calcRoeFromPbPe = (pb: number | null, pe: number | null): number | null => {
  if (pb == null || pe == null || Number.isNaN(pb) || Number.isNaN(pe) || pe === 0) {
    return null;
  }
  return (pb / pe) * 100;
};

export const calcHistHighDropPct = (
  histHigh: number | null,
  priceNow: number | null,
): number | null => {
  if (priceNow == null || histHigh == null || histHigh <= 0) return null;
  return ((priceNow - histHigh) / histHigh) * 100;
};

/** 纯数字展示（无 %），null/NaN → "—" */
export const formatDecimal = (value: number | null, precision: number = 2): string =>
  value != null && !Number.isNaN(value) ? value.toFixed(precision) : '—';

/** 可空报价格式化，null/undefined → "—" */
export const formatMarketPriceOrDash = (
  value: number | null | undefined,
  code?: string,
): string => (value != null ? formatMarketPrice(value, code) : '—');
