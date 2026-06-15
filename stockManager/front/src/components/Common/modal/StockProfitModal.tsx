import { Space, Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { HoldingStatus } from '@/components/Common/HoldingStatus';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { MarketCurrency, toMarketCurrency } from '@/utils/format/stock';
import { renderAmount } from '@/utils/format/render';
import { useCommonModal } from './useCommonModal';
import './index.less';

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
  isHkCategory?: boolean;
};

const SummaryItems: React.FC<{
  profit: number;
  loss: number;
  netIncome: number;
  currency: MarketCurrency;
}> = ({ profit, loss, netIncome, currency }) => {
  const { profitColor, lossColor } = useProfitLossColors();

  return (
    <>
      <Text>获利：{renderAmount(profit, { currency, color: profitColor })} </Text>
      <Text>亏损：{renderAmount(loss, { currency, color: lossColor })} </Text>
      <Text>净盈亏：{renderAmount(netIncome, { currency })} </Text>
    </>
  );
};

const SummaryHeader: React.FC<{
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
  currency: MarketCurrency;
}> = ({ categoryName, profit, loss, netIncome, currency }) => {
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
                currency={currency}
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
            currency={currency}
          />
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
      const { data, categoryName, profit, loss, netIncome, isHkCategory } = params;

      if (!data?.length) {
        return;
      }

      const currency: MarketCurrency = toMarketCurrency(!!isHkCategory);
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
          render: (value: number, record: StockProfitData) =>
            renderAmount(value, {
              code: record.code,
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
          currency={currency}
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
