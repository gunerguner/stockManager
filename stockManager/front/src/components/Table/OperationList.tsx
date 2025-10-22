import { Table, Tooltip } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { colorFromValue } from '@/utils';

export type OperationListProps = {
  data: API.StockData;
  showAll: boolean;
  showConv: boolean;
};

export const OperationList: React.FC<OperationListProps> = (props) => {
  /**
   * 根据筛选条件决定行是否隐藏
   */
  const rowClassName = (record: API.Stock): string => {
    const shouldHideZeroValue = record.totalValue < 0.1 && !props.showAll;
    const shouldHideConvertible = record.stockType === 'CONV' && !props.showConv;
    
    return shouldHideZeroValue || shouldHideConvertible ? 'hide' : '';
  };

  /**
   * 操作类型映射
   */
  const operationTypeMap: Record<string, string> = {
    BUY: '买入',
    SELL: '卖出',
    DV: '除权除息',
  };

  /**
   * 操作记录列定义
   */
  const columnsOperation: ColumnsType<API.Operation> = [
    {
      title: '交易日期',
      dataIndex: 'date',
    },
    {
      title: '类型',
      dataIndex: 'type',
      render: (item: string) => <div>{operationTypeMap[item] || item}</div>,
    },
    {
      title: '成交价',
      dataIndex: 'price',
    },
    {
      title: '数量',
      dataIndex: 'count',
    },
    {
      title: '佣金',
      dataIndex: 'fee',
      render: (item: number) => <div>{item?.toFixed(2)}</div>,
    },
    {
      title: '成交金额',
      dataIndex: 'sum',
      render: (item: number) => <div>{item?.toFixed(2)}</div>,
    },
    {
      title: '说明',
      dataIndex: 'comment',
    },
  ];

  /**
   * 展开行渲染函数（显示操作记录明细）
   */
  const expandedRowRender = (record: API.Stock) => (
    <Table
      style={{ margin: '10px 0' }}
      columns={columnsOperation}
      size="small"
      bordered
      tableLayout="fixed"
      dataSource={record.operationList}
      pagination={false}
    />
  );

  /**
   * 股票列表列定义
   */
  const columns: ColumnsType<API.Stock> = [
    {
      title: '名称',
      dataIndex: 'name',
      render: (_: string, record: API.Stock) => (
        <a
          target="_blank"
          href={`https://xueqiu.com/S/${record.code}`}
          style={{ textDecoration: 'none', fontWeight: 'bold', fontSize: '13px' }}
          rel="noreferrer"
        >
          {`${record.name} (${record.code})`}
        </a>
      ),
    },
    {
      title: '现价',
      dataIndex: 'priceNow',
    },
    {
      title: '涨跌',
      dataIndex: 'offsetTodayRatio',
      render: (_: string, record: API.Stock) => (
        <div style={{ color: colorFromValue(record.offsetToday) }}>
          {`${record.offsetToday.toFixed(3)} (${record.offsetTodayRatio})`}
        </div>
      ),
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      defaultSortOrder: 'descend',
      sorter: (a: API.Stock, b: API.Stock) => a.totalValue - b.totalValue,
      render: (_: number, record: API.Stock) => {
        const ratio = `${((record.totalValue / props.data.overall.totalValue) * 100).toFixed(2)}%`;
        return (
          <Tooltip title={ratio}>
            <div>{record.totalValue.toFixed(2)}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '持仓',
      dataIndex: 'holdCount',
    },
    {
      title: '摊薄成本/持仓成本',
      dataIndex: 'overallCost',
      render: (_: number, record: API.Stock) => (
        <div>{`${record.overallCost.toFixed(2)}/${record.holdCost.toFixed(2)}`}</div>
      ),
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      sorter: (a: API.Stock, b: API.Stock) => a.offsetCurrent - b.offsetCurrent,
      render: (_: number, record: API.Stock) => {
        const totalOffsetToday = record.offsetToday * record.holdCount;
        return (
          <Tooltip title={totalOffsetToday.toFixed(2)} color={colorFromValue(totalOffsetToday)}>
            <div style={{ color: colorFromValue(record.offsetCurrent) }}>
              {record.offsetCurrent.toFixed(2)}
            </div>
          </Tooltip>
        );
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      sorter: (a: API.Stock, b: API.Stock) => a.offsetTotal - b.offsetTotal,
      render: (item: number) => (
        <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>
      ),
    },
  ];

  return (
    <Table
      rowKey="code"
      columns={columns}
      dataSource={props.data.stocks}
      bordered
      pagination={false}
      rowClassName={rowClassName}
      expandable={{ expandedRowRender }}
    />
  );
};
