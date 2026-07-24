import { Space, Typography, theme } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { HoldingStatus } from '@/components/Common/HoldingStatus';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { renderAmount } from '@/utils/format/render';
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
}> = ({ profit, loss, netIncome }) => {
  const { profitColor, lossColor } = useProfitLossColors();

  return (
    <>
      <Text>获利：{renderAmount(profit, { color: profitColor })} </Text>
      <Text>亏损：{renderAmount(loss, { color: lossColor })} </Text>
      <Text>净盈亏：{renderAmount(netIncome)} </Text>
    </>
  );
};

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
  const { profitColor, lossColor } = useProfitLossColors();

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
          render: (value: number) =>
            renderAmount(value, {
              profitLossColors: { profitColor, lossColor },
            }),
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
    [showSingleTable, isMobile, profitColor, lossColor],
  );

  return { showStockProfit };
};
