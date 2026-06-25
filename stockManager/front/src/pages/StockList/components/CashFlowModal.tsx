import { Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { renderAmount } from '@/utils/format/render';
import { useCommonModal } from '@/components/Common/modal/useCommonModal';

const { Text } = Typography;

export type ShowCashFlowParams = {
  totalCashIn: number;
  cashFlowList: API.CashFlowRecord[];
};

export const useCashFlowModal = () => {
  const { showSingleTable } = useCommonModal();
  const isMobile = useIsMobile();
  const { profitColor, lossColor } = useProfitLossColors();

  const showCashFlow = React.useCallback(
    (params: ShowCashFlowParams) => {
      const { totalCashIn, cashFlowList } = params;
      const profitLossColors = { profitColor, lossColor };

      const columns: ColumnsType<API.CashFlowRecord> = [
        {
          title: '交易日期',
          dataIndex: 'date',
          width: isMobile ? 100 : 120,
        },
        {
          title: '出入金',
          dataIndex: 'amount',
          width: isMobile ? 100 : 150,
          render: (value: number) => renderAmount(value, { profitLossColors }),
        },
      ];

      const headerView = (
        <>
          <Text>净入金：</Text>
          {renderAmount(totalCashIn, { profitLossColors })}
        </>
      );

      showSingleTable({
        title: '出入金明细',
        headerView,
        columns,
        dataSource: cashFlowList,
      });
    },
    [showSingleTable, isMobile, profitColor, lossColor],
  );

  return { showCashFlow };
};
