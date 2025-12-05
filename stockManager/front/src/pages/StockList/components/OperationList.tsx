import { Table, Tooltip } from 'antd';
import { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { colorFromValue, formatPrice, renderAmount } from '@/utils/renderTool';
import { useTradeDetailModal } from '@/components/Common/TradeDetailModal';
import './index.less';

// ==================== 类型定义 ====================

type OperationListProps = {
  data: API.StockData;
  showAll: boolean;
  showConv: boolean;
};

// ==================== 组件 ====================

export const OperationList: React.FC<OperationListProps> = ({ data, showAll, showConv }) => {
  const isMobile = useIsMobile();
  const { showTradeDetail } = useTradeDetailModal();

  /** 判断行是否隐藏 */
  const shouldHideRow = (record: API.Stock) =>
    (record.totalValue < 0.1 && !showAll) || (record.stockType === 'CONV' && !showConv);

  /** 处理行点击 */
  const handleRowClick = (record: API.Stock) => {
    showTradeDetail({
      data: [{ stock: record, operations: record.operationList }],
      displayType: 'stockInfo',
    });
  };

  /** 表格列配置 */
  const columns: ColumnsType<API.Stock> = useMemo(() => [
    {
      title: '名称',
      dataIndex: 'name',
      fixed: isMobile ? false : 'left',
      render: (_, r) => (
        <Tooltip title={r.code}>
          <span className="stock-name-link">{r.name}</span>
        </Tooltip>
      ),
    },
    {
      title: '现价',
      dataIndex: 'priceNow',
      render: (v) => <div>{formatPrice(v)}</div>,
    },
    {
      title: '涨跌',
      dataIndex: 'offsetTodayRatio',
      render: (_, r) => (
        <div style={{ color: colorFromValue(r.offsetToday) }}>
          {`${formatPrice(r.offsetToday)} (${r.offsetTodayRatio})`}
        </div>
      ),
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      defaultSortOrder: 'descend',
      sorter: (a, b) => a.totalValue - b.totalValue,
      render: (_, r) => (
        <Tooltip title={`${((r.totalValue / data.overall.totalValue) * 100).toFixed(2)}%`}>
          <div>{r.totalValue.toFixed(2)}</div>
        </Tooltip>
      ),
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
      render: (_, r) => <div>{`${r.overallCost.toFixed(2)}/${r.holdCost.toFixed(2)}`}</div>,
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      sorter: (a, b) => a.offsetCurrent - b.offsetCurrent,
      render: (_, r) => {
        const todayTotal = r.offsetToday * r.holdCount;
        return (
          <Tooltip title={todayTotal.toFixed(2)} color={colorFromValue(todayTotal)}>
            <div>{renderAmount(r.offsetCurrent)}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      sorter: (a, b) => a.offsetTotal - b.offsetTotal,
      render: (v) => <div>{renderAmount(v)}</div>,
    },
  ], [isMobile, data.overall.totalValue]);

  return (
    <div className="operation-list-wrapper">
      <Table
        rowKey="code"
        columns={columns}
        dataSource={data.stocks}
        bordered
        pagination={false}
        rowClassName={(r) => (shouldHideRow(r) ? 'hide' : '')}
        onRow={(r) => ({ onClick: () => handleRowClick(r), style: { cursor: 'pointer' } })}
        scroll={isMobile ? { x: 'max-content' } : undefined}
        size={isMobile ? 'small' : 'middle'}
        tableLayout="auto"
      />
    </div>
  );
};
