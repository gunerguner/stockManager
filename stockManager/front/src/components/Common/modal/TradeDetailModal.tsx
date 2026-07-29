import { Typography, Space, Tooltip } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { HoldingStatus } from '@/components/Common/HoldingStatus';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  formatAmount,
  formatDecimalRatio,
  formatMarketPrice,
  isHkCode,
  operationComment,
  totalDividendCny,
  tradeAmountCny,
} from '@/utils/format/stock';
import { AmountText } from '@/utils/format/render';
import { useCommonModal } from './useCommonModal';
import './index.less';

const { Text } = Typography;

export type TradeDetailDisplayType = 'stockInfo' | 'tradeList';

export type ShowTradeDetailParams = {
  data: Array<{ stock: API.Stock; operations: API.Operation[] }>;
  title?: string;
  displayType: TradeDetailDisplayType;
};

const OPERATION_TYPE_MAP: Record<string, string> = {
  BUY: '买入',
  SELL: '卖出',
  DV: '除权除息',
};

const StockInfo: React.FC<{
  stock: API.Stock;
  operations: API.Operation[];
}> = ({ stock, operations }) => {
  const { colorFromValue } = useProfitLossColors();
  const dividendTotal = totalDividendCny(stock.code, operations);

  const infoItems = [
    { label: '现价', value: formatMarketPrice(stock.priceNow, stock.code) },
    { label: '持股', value: stock.holdCount },
    { label: '累计盈亏', value: <AmountText value={stock.offsetTotal} /> },
    { label: '总计分红', value: <AmountText value={dividendTotal} /> },
    {
      label: '资金加权收益率',
      value: (
        <span
          style={{
            color: colorFromValue(stock.moneyWeightedReturn),
          }}
        >
          {formatDecimalRatio(stock.moneyWeightedReturn)}
        </span>
      ),
    },
  ];

  return (
    <div className="stock-info-grid">
      {infoItems.map((item) => (
        <div className="stock-info-item" key={item.label}>
          <Text type="secondary" className="stock-info-label">
            {item.label}
          </Text>
          <Text className="stock-info-value">{item.value}</Text>
        </div>
      ))}
    </div>
  );
};

const StockHeader: React.FC<{
  stock: API.Stock;
  operations: API.Operation[];
  showStockInfo: boolean;
}> = ({ stock, operations, showStockInfo }) => {
  const stockInfo = showStockInfo ? <StockInfo stock={stock} operations={operations} /> : null;

  return (
    <div className="stock-header-wrapper">
      <div className="stock-header-left">
        <Space className="stock-identity">
          <HoldingStatus {...stock} withLink />
          <Text type="secondary">({stock.code})</Text>
        </Space>
        {stockInfo}
      </div>
      <Text
        type="secondary"
        className="trade-count"
      >
        共 {operations.length} 笔交易
      </Text>
    </div>
  );
};

export const useTradeDetailModal = () => {
  const { showMultiTable } = useCommonModal();
  const isMobile = useIsMobile();

  const showTradeDetail = React.useCallback(
    (params: ShowTradeDetailParams) => {
      const { data, title = '所有交易明细', displayType } = params;

      if (data.length === 0) {
        return;
      }

      const getColumnsOperation = (code: string): ColumnsType<API.Operation> => [
        { title: '交易日期', dataIndex: 'date', width: isMobile ? 90 : 110 },
        {
          title: '类型',
          dataIndex: 'type',
          width: isMobile ? 60 : 80,
          render: (v: string) => <div>{OPERATION_TYPE_MAP[v] || v}</div>,
        },
        {
          title: '成交价',
          dataIndex: 'price',
          width: isMobile ? 70 : 90,
          render: (v: number) => <div>{formatMarketPrice(v, code)}</div>,
        },
        { title: '数量', dataIndex: 'count', width: isMobile ? 60 : 80 },
        {
          title: '佣金',
          dataIndex: 'fee',
          width: isMobile ? 60 : 80,
          render: (v: number) => <div>{formatAmount(v)}</div>,
        },
        {
          title: '成交金额',
          dataIndex: 'price',
          key: 'tradeAmount',
          width: isMobile ? 80 : 100,
          render: (_: number, record: API.Operation) => {
            const amountCny = tradeAmountCny(code, record);
            const cell = <div>{formatAmount(amountCny)}</div>;
            // 港股买卖才展示港币名义金额；DV 的 cash 已是人民币到账口径
            if (!isHkCode(code) || record.type === 'DV') {
              return cell;
            }
            return (
              <Tooltip title={formatAmount(record.price * record.count, { currency: 'hkd' })}>
                {cell}
              </Tooltip>
            );
          },
        },
        {
          title: '说明',
          dataIndex: 'comment',
          width: isMobile ? 100 : 150,
          render: (_: string, record: API.Operation) => operationComment(record),
        },
      ];

      const tables = data.map((group, index) => {
        const showStockInfo = displayType === 'stockInfo' && index === 0;

        const headerView = (
          <StockHeader
            stock={group.stock}
            operations={group.operations}
            showStockInfo={showStockInfo}
          />
        );

        return {
          headerView,
          columns: getColumnsOperation(group.stock.code),
          dataSource: group.operations,
        };
      });

      showMultiTable({
        title,
        tables,
        width: 1200,
      });
    },
    [showMultiTable, isMobile],
  );

  return { showTradeDetail };
};
