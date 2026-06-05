import { Table, Tooltip } from 'antd';
import { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import {
  colorFromValue,
  formatMarketAmount,
  formatMarketPrice,
  isHkCode,
  toCnyAmount,
} from '@/utils/format/stock';
import { renderAmount, renderHoldingStatus } from '@/utils/format/render';
import { useTradeDetailModal } from '@/components/Common/TradeDetailModal';
import './index.less';

// ==================== 类型定义 ====================

type OperationListProps = {
  data: API.StockData;
  operations: Record<string, API.Operation[]>;
  showAll: boolean;
  showConv: boolean;
};

// ==================== 组件 ====================

export const OperationList: React.FC<OperationListProps> = ({ data, operations, showAll, showConv }) => {
  const isMobile = useIsMobile();
  const { showTradeDetail } = useTradeDetailModal();

  /** 处理行点击 */
  const handleRowClick = (record: API.Stock) => {
    showTradeDetail({
      data: [{ stock: record, operations: operations[record.code] || [] }],
      displayType: 'stockInfo',
    });
  };

  /** 预过滤数据，只传递需要显示的行到 Table */
  const filteredData = useMemo(() => {
    return data.stocks.filter(
      (record) =>
        !((record.totalValue < 0.1 && !showAll) || (record.stockType === 'CONV' && !showConv))
    );
  }, [data.stocks, showAll, showConv]);

  /** 表格列配置 */
  const columns: ColumnsType<API.Stock> = useMemo(() => [
    {
      title: '名称',
      dataIndex: 'name',
      fixed: isMobile ? false : 'left',
      render: (_, r) =>
        renderHoldingStatus({
          name: r.name,
          code: r.code,
          isProfit: r.offsetTotal > 0,
          holding: r.holdCount > 0,
          isHk: isHkCode(r.code),
          nameClassName: 'stock-name-link',
        }),
    },
    {
      title: '现价',
      dataIndex: 'priceNow',
      render: (v, r) => <div>{formatMarketPrice(v, r.code)}</div>,
    },
    {
      title: '涨跌',
      dataIndex: 'offsetTodayRatio',
      render: (_, r) => (
        <div style={{ color: colorFromValue(r.offsetToday) }}>
          {`${formatMarketPrice(r.offsetToday, r.code)} (${r.offsetTodayRatio})`}
        </div>
      ),
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      defaultSortOrder: 'descend',
      sorter: (a, b) => a.totalValue - b.totalValue,
      render: (_, r) => {
        const hkdCnyRate = data.overall.hkdCnyRate ?? 0;
        const valueCny = toCnyAmount(r.code, r.totalValue, hkdCnyRate);
        const percentage = data.overall.totalValue
          ? ((valueCny / data.overall.totalValue) * 100).toFixed(2)
          : '0.00';
        return (
          <Tooltip title={`${percentage}%`}>
            <div>{formatMarketAmount(r.totalValue, r.code)}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '持仓',
      dataIndex: 'holdCount',
      render: (_, r) => (
        <Tooltip title={`持股 ${r.holdingDuration} 天`}>
          <div>{r.holdCount}</div>
        </Tooltip>
      ),
    },
    {
      title: '摊薄/持仓成本',
      dataIndex: 'overallCost',
      render: (_, r) => (
        <div>
          {`${formatMarketAmount(r.overallCost, r.code)}/${formatMarketAmount(r.holdCost, r.code)}`}
        </div>
      ),
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      sorter: (a, b) => a.offsetCurrent - b.offsetCurrent,
      render: (_, r) => {
        const todayTotal = r.offsetToday * r.holdCount;
        return (
          <Tooltip
            title={formatMarketAmount(todayTotal, r.code)}
            color={colorFromValue(todayTotal)}
          >
            <div>{renderAmount(r.offsetCurrent, undefined, 2, r.code)}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      sorter: (a, b) => a.offsetTotal - b.offsetTotal,
      render: (_, r) => (
        <div style={{ color: colorFromValue(r.offsetTotal) }}>
          {`${formatMarketAmount(r.offsetTotal, r.code)} (${r.moneyWeightedReturn})`}
        </div>
      ),
    },
  ], [isMobile, data.overall.totalValue]);

  return (
    <div className="operation-list-wrapper">
      <Table
        rowKey="code"
        columns={columns}
        dataSource={filteredData}
        bordered
        pagination={false}
        onRow={(r) => ({ onClick: () => handleRowClick(r), style: { cursor: 'pointer' } })}
        scroll={isMobile ? { x: 'max-content' } : undefined}
        size={isMobile ? 'small' : 'middle'}
        tableLayout="auto"
      />
    </div>
  );
};
