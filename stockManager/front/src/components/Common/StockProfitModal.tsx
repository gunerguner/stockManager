import { Space, Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { renderAmount, renderHoldingStatus } from '@/utils/format/render';
import { isHkCode } from '@/utils/format/stock';
import { useCommonModal } from './useCommonModal';
import './index.less';

const { Text } = Typography;

// ==================== 类型定义 ====================

export interface StockProfitData {
  code: string;
  name: string;
  netIncome: number;
  holdCount?: number;
}

export type ShowStockProfitParams = {
  data: StockProfitData[];
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
  isHkCategory?: boolean;
};

// ==================== 组件 ====================

/** 汇总信息项 */
const SummaryItems: React.FC<{
  profit: number;
  loss: number;
  netIncome: number;
  amountCode?: string;
}> = ({ profit, loss, netIncome, amountCode }) => (
  <>
    <Text>获利：{renderAmount(profit, 'red', 2, amountCode)} </Text>
    <Text>亏损：{renderAmount(loss, 'green', 2, amountCode)} </Text>
    <Text>净盈亏：{renderAmount(netIncome, undefined, 2, amountCode)} </Text>
  </>
);

/** 汇总信息头部 */
const SummaryHeader: React.FC<{
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
  amountCode?: string;
}> = ({ categoryName, profit, loss, netIncome, amountCode }) => {
  const isMobile = useIsMobile();

  return (
    <>
      {isMobile ? (
        <>
          <div className="category-name">
            <strong>{categoryName}</strong>
          </div>
          <div className="modal-info-row">
            <Space size="small" wrap>
              <SummaryItems
                profit={profit}
                loss={loss}
                netIncome={netIncome}
                amountCode={amountCode}
              />
            </Space>
          </div>
        </>
      ) : (
        <Space size="middle" wrap>
          <strong>{categoryName}</strong>
          <SummaryItems
            profit={profit}
            loss={loss}
            netIncome={netIncome}
            amountCode={amountCode}
          />
        </Space>
      )}
    </>
  );
};

// ==================== Hook ====================

export const useStockProfitModal = () => {
  const { showSingleTable } = useCommonModal();
  const isMobile = useIsMobile();

  const showStockProfit = React.useCallback(
    (params: ShowStockProfitParams) => {
      const { data, categoryName, profit, loss, netIncome, isHkCategory } = params;

      if (!data?.length) {
        return;
      }

      const amountCode = isHkCategory ? 'hk00000' : undefined;
      const sortedData = [...data].sort((a, b) => b.netIncome - a.netIncome);

      const columns: ColumnsType<StockProfitData> = [
        {
          title: '股票名称',
          dataIndex: 'name',
          width: isMobile ? 120 : 200,
          render: (_name: string, record: StockProfitData) =>
            renderHoldingStatus({
              name: record.name,
              code: record.code,
              isProfit: record.netIncome > 0,
              holding: (record.holdCount ?? 0) > 0,
              isHk: isHkCode(record.code),
            }),
        },
        {
          title: '净盈亏',
          dataIndex: 'netIncome',
          width: isMobile ? 100 : 150,
          render: (value: number, record: StockProfitData) =>
            renderAmount(value, undefined, 2, record.code),
        },
      ];

      const headerView = (
        <SummaryHeader
          categoryName={categoryName}
          profit={profit}
          loss={loss}
          netIncome={netIncome}
          amountCode={amountCode}
        />
      );

      showSingleTable({
        title: '盈亏明细',
        headerView,
        columns,
        dataSource: sortedData,
      });
    },
    [showSingleTable, isMobile],
  );

  return { showStockProfit };
};

