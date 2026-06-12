import type { CSSProperties } from 'react';
import { theme } from 'antd';
import { useMemo } from 'react';
import type { GlobalToken } from 'antd/es/theme/interface';

export type ProfitLossColors = {
  profitColor: string;
  lossColor: string;
  colorFromValue: (value: number) => string | undefined;
  highlightStyle: CSSProperties;
};

export function getProfitLossColors(token: GlobalToken): ProfitLossColors {
  return {
    profitColor: token.colorError,
    lossColor: token.colorSuccess,
    colorFromValue: (value: number) =>
      value > 0 ? token.colorError : value < 0 ? token.colorSuccess : undefined,
    highlightStyle: {
      color: token.colorError,
      fontWeight: 600,
      background: token.colorErrorBg,
      padding: '2px 6px',
      borderRadius: token.borderRadius,
    },
  };
}

export function useProfitLossColors(): ProfitLossColors {
  const { token } = theme.useToken();
  return useMemo(() => getProfitLossColors(token), [token]);
}
