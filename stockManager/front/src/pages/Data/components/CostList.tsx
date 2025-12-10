import { Table, Statistic } from 'antd';
import React, { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useTradeDetailModal } from '@/components/Common/TradeDetailModal';
import './index.less';

// ==================== 类型定义 ====================

type CostPeriodType = 'year' | 'month';

interface CostListModel {
  id: string;
  type: CostPeriodType;
  normalTradeCount: number;
  convTradeCount: number;
  dividendCount: number;
  fee: number;
  subList?: CostListModel[];
}

export type CostListProps = {
  data: API.Stock[];
  totalCost: number;
};

// ==================== 配置 ====================

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

// ==================== 工具函数 ====================

/** 创建空的统计记录 */
const createEmptyRecord = (id: string, type: CostPeriodType): CostListModel => ({
  id,
  type,
  normalTradeCount: 0,
  convTradeCount: 0,
  dividendCount: 0,
  fee: 0,
  subList: type === 'year' ? [] : undefined,
});

/** 统计交易数据 */
const buildCostList = (data: API.Stock[]): CostListModel[] => {
  const yearMap = new Map<string, CostListModel>();

  for (const stock of data) {
    for (const op of stock.operationList) {
      const [year, month] = [op.date.substring(0, 4), op.date.substring(5, 7)];

      // 获取或创建年份记录
      if (!yearMap.has(year)) yearMap.set(year, createEmptyRecord(year, 'year'));
      const yearRecord = yearMap.get(year)!;

      // 获取或创建月份记录
      let monthRecord = yearRecord.subList!.find((m) => m.id === month);
      if (!monthRecord) {
        monthRecord = createEmptyRecord(month, 'month');
        yearRecord.subList!.push(monthRecord);
      }

      // 统计数据
      if (op.type === 'DV') {
        yearRecord.dividendCount++;
        monthRecord.dividendCount++;
      } else if (stock.stockType === 'CONV') {
        yearRecord.convTradeCount++;
        monthRecord.convTradeCount++;
        yearRecord.fee += op.fee;
        monthRecord.fee += op.fee;
      } else {
        yearRecord.normalTradeCount++;
        monthRecord.normalTradeCount++;
        yearRecord.fee += op.fee;
        monthRecord.fee += op.fee;
      }
    }
  }

  // 排序并返回
  const result = [...yearMap.values()].sort((a, b) => Number(a.id) - Number(b.id));
  result.forEach((year) => year.subList?.sort((a, b) => Number(a.id) - Number(b.id)));
  return result;
};

// ==================== 组件 ====================

export const CostList: React.FC<CostListProps> = ({ data, totalCost }) => {
  const isMobile = useIsMobile();
  const { showTradeDetail } = useTradeDetailModal();

  /** 统计数据 */
  const costList = useMemo(() => buildCostList(data), [data]);

  /** 筛选交易记录并打开详情弹窗 */
  const handleCellClick = (record: CostListModel, dataIndex: keyof CostListModel, parentYear?: string) => {
    const isYearRow = record.type === 'year';
    const year = isYearRow ? record.id : parentYear;
    const month = isYearRow ? '' : record.id;
    if (!year) return;

    const filter = TRADE_FILTERS[dataIndex];
    if (!filter) return;

    // 筛选符合条件的交易
    const filteredData = data
      .map((stock) => ({
        stock,
        operations: stock.operationList.filter((op) => {
          const [opYear, opMonth] = [op.date.substring(0, 4), op.date.substring(5, 7)];
          return opYear === year && (!month || opMonth === month) && filter(stock, op);
        }),
      }))
      .filter((item) => item.operations.length > 0);

    if (filteredData.length === 0) return;

    const label = TRADE_COLUMNS.find(([key]) => key === dataIndex)?.[1].replace('次数', '') || '';
    showTradeDetail({
      data: filteredData,
      title: `${year}年${month ? `${month}月` : ''}交易明细 - ${label}`,
      displayType: 'tradeList'
    });
  };

  /** 生成表格列配置 */
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
          <span className="clickable-cell" onClick={() => handleCellClick(record, dataIndex, parentYear)}>
            {value}
          </span>
        ),
    })),
    {
      title: '费用',
      dataIndex: 'fee',
      render: (value: number) => <span>{value.toFixed(2)}</span>,
    },
  ];

  /** 展开行渲染 */
  const expandedRowRender = (record: CostListModel) => (
    <Table
      className="expanded-row-table"
      rowKey="id"
      columns={getColumns(record.id)}
      dataSource={record.subList}
      bordered
      size="small"
      tableLayout="auto"
      pagination={false}
      showHeader={false}
      scroll={isMobile ? { x: 'max-content' } : undefined}
    />
  );

  return (
    <div className="cost-list-wrapper">
      <div className="cost-list-header">
        <Statistic
          title="总费用"
          value={totalCost}
          precision={2}
          styles={isMobile ? {
            title: { fontSize: 12 },
            content: { fontSize: 18 },
          }:{}}
        />
      </div>
      <div className="cost-list-table-container">
        <Table
          rowKey="id"
          columns={getColumns()}
          dataSource={costList}
          bordered
          pagination={false}
          expandable={{ expandedRowRender }}
          scroll={isMobile ? { x: 'max-content' } : undefined}
          size={isMobile ? 'small' : 'middle'}
          tableLayout="auto"
        />
      </div>
    </div>
  );
};
