import React from 'react';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { formatAmount, formatDecimalRatio, formatMarketPrice } from './stock';

type AmountTextProps = {
  value: number;
};

/** 金额文本：根据数值自动着色（正红负绿） */
export const AmountText: React.FC<AmountTextProps> = ({ value }) => {
  const { colorFromValue } = useProfitLossColors();
  return <span style={{ color: colorFromValue(value) }}>{formatAmount(value)}</span>;
};

type DailyChangeCellProps = React.HTMLAttributes<HTMLDivElement> & {
  offsetToday: number;
  offsetTodayRatio: number;
  code: string;
};

/** 当日涨跌单元格：根据涨跌自动着色（正红负绿） */
export const DailyChangeCell = React.forwardRef<HTMLDivElement, DailyChangeCellProps>(
  function DailyChangeCell(
    { offsetToday, offsetTodayRatio, code, className = 'cell-number', style, ...props },
    ref,
  ) {
    const { colorFromValue } = useProfitLossColors();
    return (
      <div
        ref={ref}
        {...props}
        className={className}
        style={{ color: colorFromValue(offsetToday), ...style }}
      >
        {`${formatMarketPrice(offsetToday, code)} (${formatDecimalRatio(offsetTodayRatio)})`}
      </div>
    );
  },
);
