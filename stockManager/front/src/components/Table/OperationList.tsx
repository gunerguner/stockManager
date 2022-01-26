import { Table, Tooltip } from 'antd';
import React from 'react';

import { ColumnsType } from 'antd/lib/table';
import { colorFromValue } from '../../utils';

export type OperationListProps = {
  data: API.StockData;
  showAll: boolean;
};

export const OperationList: React.FC<OperationListProps> = (props: OperationListProps) => {
  const rowClassName = (record: API.Stock, index: number): string => {
    return record.totalValue < 0.1 && !props.showAll ? 'hide' : '';
  };

  const expandedRowRender = (record: API.Stock) => {
    return (
      <Table
        style={{ marginTop: '10px', marginBottom: '10px' }}
        columns={ColumnsOperation}
        size="small"
        bordered
        tableLayout="fixed"
        dataSource={record.operationList}
        pagination={false}
      ></Table>
    );
  };

  const Columns: ColumnsType<API.Stock> = [
    {
      title: '名称',
      dataIndex: 'name',
      render: (value: any, record: API.Stock, index: number) => {
        return (
          <a
            target="_blank"
            href={'https://xueqiu.com/S/' + record.code}
            style={{ textDecoration: 'none', fontWeight: 'bold', fontSize: '13px' }}
          >
            {record.name + ' (' + record.code + ')'}
          </a>
        );
      },
    },
    {
      title: '现价',
      dataIndex: 'priceNow',
    },
    {
      title: '涨跌',
      dataIndex: 'offsetTodayRatio',
      render: (value: any, record: API.Stock, index: number) => {
        return (
          <div style={{ color: colorFromValue(record.offsetToday) }}>
            {record?.offsetToday.toFixed(3) + ' (' + record?.offsetTodayRatio + ' )'}
          </div>
        );
      },
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      defaultSortOrder: 'descend',
      sorter: (a: API.Stock, b: API.Stock) => {
        return a.totalValue - b.totalValue;
      },
      render: (value: any, record: API.Stock, index: number) => {
        const ratio = ((record.totalValue / props.data.overall.totalValue)*100).toFixed(2) + '%'
        return ( <Tooltip title={ratio} >
          <div>{record?.totalValue.toFixed(2)}</div>
          </Tooltip>
        )
       
      },
    },
    {
      title: '持仓',
      dataIndex: 'holdCount',
    },
    {
      dataIndex: 'overallCost',
      render: (value: any, record: API.Stock, index: number) => {
        return <div>{record?.overallCost.toFixed(2) + '/' + record?.holdCost.toFixed(2)}</div>;
      },
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      sorter: (a: API.Stock, b: API.Stock) => {
        return a.offsetCurrent - b.offsetCurrent;
      },
      render: (value: any, record: API.Stock, index: number) => {
        const totalOffsetToday = record.offsetToday * record.holdCount;
        const item = record.offsetCurrent;
        return (
          <Tooltip title={totalOffsetToday.toFixed(2)} color={colorFromValue(totalOffsetToday)}>
            <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      sorter: (a: API.Stock, b: API.Stock) => {
        return a.offsetTotal - b.offsetTotal;
      },
      render: (item: number) => {
        return <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>;
      },
    },
  ];

  const ColumnsOperation: ColumnsType<API.Operation> = [
    {
      title: '交易日期',
      dataIndex: 'date',
    },
    {
      title: '类型',
      dataIndex: 'type',
      render: (item: string) => {
        return <div>{item == 'BUY' ? '买入' : item == 'SELL' ? '卖出' : '除权除息'}</div>;
      },
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
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '成交金额',
      dataIndex: 'sum',
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '说明',
      dataIndex: 'comment',
    },
  ];

  return (
    <Table
      rowKey="code"
      columns={Columns}
      dataSource={props.data.stocks}
      bordered
      pagination={false}
      rowClassName={rowClassName}
      expandable={{ expandedRowRender }}
    />
  );
};
