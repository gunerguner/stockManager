import React from 'react';
import { formatAmount, formatDecimalRatio, formatMarketPrice, FormatAmountOptions } from './stock';

export type ProfitLossColorOptions = {
  profitColor: string;
  lossColor: string;
};

const colorFromProfitLoss = (
  value: number,
  colors: ProfitLossColorOptions,
): string | undefined =>
  value > 0 ? colors.profitColor : value < 0 ? colors.lossColor : undefined;

export type RenderAmountOptions = FormatAmountOptions & {
  color?: string;
  profitLossColors?: ProfitLossColorOptions;
};

export const renderAmount = (value: number, options?: RenderAmountOptions): React.ReactNode => {
  const { color, profitLossColors, ...formatOptions } = options ?? {};
  const displayColor =
    color ?? (profitLossColors ? colorFromProfitLoss(value, profitLossColors) : undefined);
  return (
    <span style={{ color: displayColor }}>{formatAmount(value, formatOptions)}</span>
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
