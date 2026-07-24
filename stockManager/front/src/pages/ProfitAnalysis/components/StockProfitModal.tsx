import { Space, Typography, theme } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { HoldingStatus } from '@/components/Common/HoldingStatus';
import { useIsMobile } from '@/hooks/useIsMobile';
import { AmountText } from '@/utils/format/render';
import { useCommonModal } from '@/components/Common/modal/useCommonModal';

const { Text } = Typography;

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
};

const SummaryItems: React.FC<{
  profit: number;
  loss: number;
  netIncome: number;
}> = ({ profit, loss, netIncome }) => (
  <>
    <Text>获利：<AmountText value={profit} /> </Text>
    <Text>亏损：<AmountText value={loss} /> </Text>
    <Text>净盈亏：<AmountText value={netIncome} /> </Text>
  </>
);

const SummaryHeader: React.FC<{
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
}> = ({ categoryName, profit, loss, netIncome }) => {
  const isMobile = useIsMobile();
  const { token } = theme.useToken();

  const infoRowStyle: React.CSSProperties = {
    paddingTop: 8,
    borderTop: `1px solid ${token.colorBorderSecondary}`,
  };

  return (
    <>
      {isMobile ? (
        <>
          <div className="category-name">
            <strong>{categoryName}</strong>
          </div>
          <div style={infoRowStyle}>
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
          render: (_name: string, record: StockProfitData) => <HoldingStatus {...record} />,
        },
        {
          title: '净盈亏',
          dataIndex: 'netIncome',
          width: isMobile ? 100 : 150,
          render: (value: number) => <AmountText value={value} />,
        },
      ];

      const headerView = (
        <SummaryHeader
          categoryName={categoryName}
          profit={profit}
          loss={loss}
          netIncome={netIncome}
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
