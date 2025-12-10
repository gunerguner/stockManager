import { Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { renderAmount } from '@/utils/renderTool';
import { useCommonModal } from './useCommonModal';

const { Text } = Typography;

// ==================== 类型定义 ====================

export type ShowCashFlowParams = {
  totalCashIn: number;
  cashFlowList: API.CashFlowRecord[];
};

// ==================== Hook ====================

export const useCashFlowModal = () => {
  const { showSingleTable } = useCommonModal();
  const isMobile = useIsMobile();

  const showCashFlow = React.useCallback(
    (params: ShowCashFlowParams) => {
      const { totalCashIn, cashFlowList } = params;

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
          render: (value: number) => renderAmount(value),
        },
      ];

      const headerView = (
        <>
          <Text>净入金：</Text>
          {renderAmount(totalCashIn)}
        </>
      );

      showSingleTable({
        title: '出入金明细',
        headerView,
        columns,
        dataSource: cashFlowList,
      });
    },
    [showSingleTable, isMobile],
  );

  return { showCashFlow };
};

