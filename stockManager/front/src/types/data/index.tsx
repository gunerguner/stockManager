import { ColumnsType } from 'antd/lib/table';

export interface analysisModel {
  type: string;
  count: number;
  profit: number;
  loss: number;
  netIncome: number;
}

export const analysisColumn: ColumnsType<any> = [
  {
    title: '类型',
    dataIndex: 'type',
    render: (item: number) => {
      return <div style={{ fontWeight: 'bold' }}>{item}</div>;
    },
  },
  {
    title: '数量',
    dataIndex: 'count',
  },
  {
    title: '获利',
    dataIndex: 'profit',
    render: (item: number) => {
      return <div style={{ color: 'red' }}>{item?.toFixed(2)}</div>;
    },
    sorter: (a: analysisModel, b: analysisModel) => {
      return a.profit - b.profit;
    },
  },
  {
    title: '亏损',
    dataIndex: 'loss',
    render: (item: number) => {
      return <div style={{ color: 'green' }}>{item?.toFixed(2)}</div>;
    },
    sorter: (a: analysisModel, b: analysisModel) => {
      return a.loss - b.loss;
    },
  },
  {
    title: '净收益',
    dataIndex: 'netIncome',
    render: (item: number) => {
      const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
      return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
    },
    sorter: (a: analysisModel, b: analysisModel) => {
      return a.netIncome - b.netIncome;
    },
  },
];