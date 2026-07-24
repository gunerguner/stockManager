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

type DailyChangeCellProps = {
  offsetToday: number;
  offsetTodayRatio: number;
  code: string;
};

/** 当日涨跌单元格：根据涨跌自动着色（正红负绿） */
export const DailyChangeCell: React.FC<DailyChangeCellProps> = ({
  offsetToday,
  offsetTodayRatio,
  code,
}) => {
  const { colorFromValue } = useProfitLossColors();
  return (
    <div className="cell-number" style={{ color: colorFromValue(offsetToday) }}>
      {`${formatMarketPrice(offsetToday, code)} (${formatDecimalRatio(offsetTodayRatio)})`}
    </div>
  );
};
