import { Table, Statistic, Typography } from 'antd';
import React, { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useTradeDetailModal } from '@/components/Common/modal/TradeDetailModal';
import { buildCostListByPeriod, parseYearMonth, type CostListModel } from './costStat';
import { getHeaderStatisticStyles } from './statisticStyles';
import { formatAmount } from '@/utils/format/stock';
import './index.less';

const { Link } = Typography;

export type CostListProps = {
  data: API.Stock[];
  operations: Record<string, API.Operation[]>;
  totalCost: number;
  hkdCnyRate?: number;
  loading?: boolean;
};

/** 交易类型列配置：[dataIndex, 完整标题, 移动端标题] */
const TRADE_COLUMNS: Array<[keyof CostListModel, string, string]> = [
  ['normalTradeCount', '普通交易次数', '普通'],
  ['convTradeCount', '可转债交易次数', '转债'],
  ['dividendCount', '除权除息次数', '除权'],
];

/** 交易类型过滤条件 */
const TRADE_FILTERS: Record<string, (stock: API.Stock, op: API.Operation) => boolean> = {
  normalTradeCount: (stock, op) => stock.stockType !== 'CONV' && op.type !== 'DV',
  convTradeCount: (stock, op) => stock.stockType === 'CONV' && op.type !== 'DV',
  dividendCount: (_, op) => op.type === 'DV',
};

export const CostList: React.FC<CostListProps> = ({
  data,
  operations,
  totalCost,
  hkdCnyRate = 0,
  loading = false,
}) => {
  const isMobile = useIsMobile();
  const { showTradeDetail } = useTradeDetailModal();

  const costList = useMemo(
    () => buildCostListByPeriod(data, operations, hkdCnyRate),
    [data, operations, hkdCnyRate],
  );

  const handleCellClick = (record: CostListModel, dataIndex: keyof CostListModel, parentYear?: string) => {
    const isYearRow = record.type === 'year';
    const year = isYearRow ? record.id : parentYear;
    const month = isYearRow ? '' : record.id;
    if (!year) return;

    const filter = TRADE_FILTERS[dataIndex];
    if (!filter) return;

    const filteredData = data
      .map((stock) => ({
        stock,
        operations: (operations[stock.code] || []).filter((op) => {
          const { year: opYear, month: opMonth } = parseYearMonth(op.date);
          return opYear === year && (!month || opMonth === month) && filter(stock, op);
        }),
      }))
      .filter((item) => item.operations.length > 0);

    if (filteredData.length === 0) return;

    const label = TRADE_COLUMNS.find(([key]) => key === dataIndex)?.[1].replace('次数', '') || '';
    showTradeDetail({
      data: filteredData,
      title: `${year}年${month ? `${month}月` : ''}交易明细 - ${label}`,
      displayType: 'tradeList',
    });
  };

  const getColumns = (parentYear?: string): ColumnsType<CostListModel> => [
    {
      title: '年份',
      dataIndex: 'id',
      render: (text: string) => <strong>{text}</strong>,
    },
    ...TRADE_COLUMNS.map(([dataIndex, title, mobileTitle]) => ({
      title: isMobile ? mobileTitle : title,
      dataIndex,
      render: (value: number, record: CostListModel) =>
        value === 0 ? (
          <span>0</span>
        ) : (
          <Link onClick={() => handleCellClick(record, dataIndex, parentYear)}>{value}</Link>
        ),
    })),
    {
      title: '费用',
      dataIndex: 'fee',
      render: (value: number) => <span>{formatAmount(value)}</span>,
    },
  ];

  const expandedRowRender = (record: CostListModel) => (
    <Table
      className="expanded-row-table"
      rowKey="id"
      columns={getColumns(record.id)}
      dataSource={record.subList}
      size="small"
      tableLayout="auto"
      pagination={false}
      showHeader={false}
      scroll={isMobile ? { x: 'max-content' } : undefined}
    />
  );

  return (
    <div className="table-list-wrapper cost-list-wrapper">
      <div className="table-list-header">
        <Statistic title="总费用" value={totalCost} precision={2} styles={getHeaderStatisticStyles(isMobile)} />
      </div>
      <Table
        rowKey="id"
        columns={getColumns()}
        dataSource={costList}
        loading={loading}
        pagination={false}
        expandable={{ expandedRowRender }}
        {...getResponsiveTableProps(isMobile)}
      />
    </div>
  );
};
