import { ColumnsType } from 'antd/lib/table';

export const ColumnsOverAll: ColumnsType<API.Overall> = [
  {
    title: '当日盈亏',
    dataIndex: 'offsetToday',
    render: (item: number) => {
      const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '浮动盈亏',
    dataIndex: 'offsetCurrent',
    render: (item: number) => {
      const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '累计盈亏',
    dataIndex: 'offsetTotal',
    render: (item: number) => {
      const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '市值',
    dataIndex: 'totalValue',
    render: (item: number) => {
      const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '现金',
    dataIndex: 'totalCash',
    render: (item: number) => {
      return <div>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '本金',
    dataIndex: 'originCash',
    render: (item: number) => {
      return <div>{item?.toFixed(2)}</div>;
    },
  },
];

export const Columns: ColumnsType<API.Stock> = [
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
      const color = record.offsetToday > 0 ? 'red' : record.offsetToday < 0 ? 'green' : 'black';
      return (
        <div style={{ color: color }}>
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
    render: (item: number) => {
      return <div>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '持仓',
    dataIndex: 'holdCount',
  },
  {
    title: '摊薄成本/持仓成本',
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
    render: (item: number) => {
      const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
  },
  {
    title: '累计盈亏',
    dataIndex: 'offsetTotal',
    sorter: (a: API.Stock, b: API.Stock) => {
      return a.offsetTotal - b.offsetTotal;
    },
    render: (item: number) => {
      const color = item > 0 ? 'red' : 'green';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
  },
];

export const ColumnsOperation: ColumnsType<API.Operation> = [
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
