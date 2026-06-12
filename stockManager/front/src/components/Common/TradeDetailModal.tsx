import { Typography, Space, Divider } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  formatAmount,
  formatMarketPrice,
  formatPercent,
  isHkCode,
  toXueqiuStockUrl,
} from '@/utils/format/stock';
import { renderAmount, renderHoldingStatus } from '@/utils/format/render';
import { useCommonModal } from './useCommonModal';
import './index.less';

const { Text } = Typography;

// ==================== 类型定义 ====================

export type TradeDetailDisplayType = 'stockInfo' | 'tradeList';

export type ShowTradeDetailParams = {
  data: Array<{ stock: API.Stock; operations: API.Operation[] }>;
  title?: string;
  displayType: TradeDetailDisplayType;
};

// ==================== 常量 ====================

const OPERATION_TYPE_MAP: Record<string, string> = {
  BUY: '买入',
  SELL: '卖出',
  DV: '除权除息',
};

// ==================== 组件 ====================

/** 股票信息（通用） */
const StockInfo: React.FC<{ stock: API.Stock; isMobile: boolean }> = ({ stock, isMobile }) => {
  const { colorFromValue } = useProfitLossColors();

  const infoItems = (
    <>
      <Text>现价：{formatMarketPrice(stock.priceNow, stock.code)} </Text>
      <Text>持股：{stock.holdCount} </Text>
      <Text>累计盈亏：{renderAmount(stock.offsetTotal, { code: stock.code })} </Text>
      <Text>
        资金加权收益率：
        <span
          style={{
            color: colorFromValue(stock.moneyWeightedReturn),
          }}
        >
          {formatPercent(stock.moneyWeightedReturn * 100)}
        </span>
      </Text>
    </>
  );

  return isMobile ? (
    <div className="modal-info-row">
      <Space size="small" wrap>
        {infoItems}
      </Space>
    </div>
  ) : (
    <>
      <Divider orientation="vertical" />
      {infoItems}
    </>
  );
};

/** 股票头部组件 */
const StockHeader: React.FC<{
  stock: API.Stock;
  operationsCount: number;
  showStockInfo: boolean;
}> = ({ stock, operationsCount, showStockInfo }) => {
  const isMobile = useIsMobile();
  const { profitColor, lossColor } = useProfitLossColors();
  const stockInfo = showStockInfo ? <StockInfo stock={stock} isMobile={isMobile} /> : null;

  return (
    <div className="stock-header-wrapper">
      <div className="stock-header-left">
        <Space wrap={isMobile} className={isMobile && showStockInfo ? 'stock-header-space' : ''}>
          {renderHoldingStatus({
            name: stock.name,
            code: stock.code,
            link: toXueqiuStockUrl(stock.code),
            isProfit: stock.offsetTotal > 0,
            holding: stock.holdCount > 0,
            isHk: isHkCode(stock.code),
            profitColor,
            lossColor,
          })}
          <Text type="secondary">({stock.code})</Text>
          {!isMobile && stockInfo}
        </Space>
        {isMobile && stockInfo}
      </div>
      <Text type="secondary" className="trade-count">
        共 {operationsCount} 笔交易
      </Text>
    </div>
  );
};

// ==================== Hook ====================

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
          render: (v: number) => <div>{formatAmount(v, { code })}</div>,
        },
        {
          title: '成交金额',
          dataIndex: 'sum',
          width: isMobile ? 80 : 100,
          render: (v: number) => <div>{formatAmount(v, { code })}</div>,
        },
        { title: '说明', dataIndex: 'comment', width: isMobile ? 100 : 150 },
      ];

      const tables = data.map((group, index) => {
        const showStockInfo = displayType === 'stockInfo' && index === 0;

        const headerView = (
          <StockHeader
            stock={group.stock}
            operationsCount={group.operations.length}
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
        width: 1200
      });
    },
    [showMultiTable, isMobile],
  );

  return { showTradeDetail };
};
