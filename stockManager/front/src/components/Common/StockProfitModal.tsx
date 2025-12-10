import { Space, Tooltip, Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { renderAmount } from '@/utils/renderTool';
import { useCommonModal } from './useCommonModal';
import './index.less';

const { Text } = Typography;

// ==================== 类型定义 ====================

export interface StockProfitData {
  code: string;
  name: string;
  netIncome: number;
}

export type ShowStockProfitParams = {
  data: StockProfitData[];
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
};

// ==================== 组件 ====================

/** 汇总信息项 */
const SummaryItems: React.FC<{ profit: number; loss: number; netIncome: number }> = ({
  profit,
  loss,
  netIncome,
}) => (
  <>
    <Text>获利：{renderAmount(profit, 'red')} </Text>
    <Text>亏损：{renderAmount(loss, 'green')} </Text>
    <Text>净盈亏：{renderAmount(netIncome)} </Text>
  </>
);

/** 汇总信息头部 */
const SummaryHeader: React.FC<{
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
}> = ({ categoryName, profit, loss, netIncome }) => {
  const isMobile = useIsMobile();

  return (
    <>
      {isMobile ? (
        <>
          <div className="category-name">
            <strong>{categoryName}</strong>
          </div>
          <div className="summary-info-row">
            <Space size="small" wrap>
              <SummaryItems profit={profit} loss={loss} netIncome={netIncome} />
            </Space>
          </div>
        </>
      ) : (
        <Space size="middle" wrap>
          <strong>{categoryName}</strong>
          <SummaryItems profit={profit} loss={loss} netIncome={netIncome} />
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
      const { data, categoryName, profit, loss, netIncome } = params;

      if (!data?.length) {
        return;
      }

      const sortedData = [...data].sort((a, b) => b.netIncome - a.netIncome);

      const columns: ColumnsType<StockProfitData> = [
        {
          title: '股票名称',
          dataIndex: 'name',
          width: isMobile ? 120 : 200,
          render: (name: string, record: StockProfitData) => (
            <Tooltip title={record.code}>
              <span>{name}</span>
            </Tooltip>
          ),
        },
        {
          title: '净盈亏',
          dataIndex: 'netIncome',
          width: isMobile ? 100 : 150,
          render: (value: number) => renderAmount(value),
        },
      ];

      const headerView = (
        <SummaryHeader categoryName={categoryName} profit={profit} loss={loss} netIncome={netIncome} />
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

