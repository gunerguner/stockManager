import React from 'react';
import {
  colorFromValue,
  formatAmount,
  formatDecimalRatio,
  formatMarketPrice,
  FormatAmountOptions,
} from './stock';

export type ProfitLossColorOptions = {
  profitColor?: string;
  lossColor?: string;
};

export const renderAmount = (
  value: number,
  options?: FormatAmountOptions,
  color?: string,
  precision: number = 2,
  profitLossColors?: ProfitLossColorOptions,
): React.ReactNode => {
  const displayColor = color || colorFromValue(value, profitLossColors);
  return (
    <span style={{ color: displayColor }}>{formatAmount(value, options, precision)}</span>
  );
};

export type RenderCellOptions = {
  className?: string;
  /** When null, show dash instead of formatted value */
  priceNow?: number | null;
};

export const renderDailyChange = (
  offsetToday: number,
  offsetTodayRatio: number,
  code: string,
  colorFromValueFn: (value: number) => string | undefined,
  options?: RenderCellOptions,
): React.ReactNode => {
  if (options?.priceNow === null) return '—';

  const className = options?.className ?? 'cell-number';
  return (
    <div className={className} style={{ color: colorFromValueFn(offsetToday) }}>
      {`${formatMarketPrice(offsetToday, code)} (${formatDecimalRatio(offsetTodayRatio)})`}
    </div>
  );
};
