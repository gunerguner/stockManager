import React, { useState, useEffect } from 'react';
import ProCard from '@ant-design/pro-card';

import { Tabs, Table } from 'antd';
import { history, useModel } from 'umi';

import { ColumnsType } from 'antd/lib/table';

const { TabPane } = Tabs;

import { analysisModel } from '../../types/data';

export default (): React.ReactNode => {
  const { stock, setStockData } = useModel('stocks');

  const [analysisList, setAnalysisList] = useState([] as analysisModel[]);

  useEffect(() => {
    initializeAnalysis();
  }, []);

  const initializeAnalysis = () => {
    var analysis: analysisModel[] = [];

    const stockLists = stock.stocks;

    var isNewProfit = 0,
      isNewLoss = 0,
      isNewCount = 0,
      fundABProfit = 0,
      fundABLoss = 0,
      fundABCount = 0,
      fundInProfit = 0,
      fundInLoss = 0,
      fundInCount = 0,
      convProfit = 0,
      convLoss = 0,
      convCount = 0,
      sh60Profit = 0,
      sh60Loss = 0,
      sh60Count = 0,
      sz00Profit = 0,
      sz00Loss = 0,
      sz00Count = 0,
      sz300Profit = 0,
      sz300Loss = 0,
      sz300Count = 0,
      sh688Profit = 0,
      sh688Loss = 0,
      sh688Count = 0;

    for (const stock of stockLists) {
      isNewProfit += stock.isNew && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      isNewLoss += stock.isNew && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      isNewCount += stock.isNew ? 1 : 0;

      fundABProfit += stock.stockType == 'FUNDAB' && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      fundABLoss += stock.stockType == 'FUNDAB' && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      fundABCount += stock.stockType == 'FUNDAB' ? 1 : 0;

      fundInProfit += stock.stockType == 'FUNDIN' && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      fundInLoss += stock.stockType == 'FUNDIN' && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      fundInCount += stock.stockType == 'FUNDIN' ? 1 : 0;

      convProfit += stock.stockType == 'CONV' && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      convLoss += stock.stockType == 'CONV' && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      convCount += stock.stockType == 'CONV' ? 1 : 0;

      sh60Profit +=
        stock.stockType == 'SH60' && !stock.isNew && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      sh60Loss +=
        stock.stockType == 'SH60' && !stock.isNew && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      sh60Count += stock.stockType == 'SH60' && !stock.isNew ? 1 : 0;

      sz00Profit +=
        stock.stockType == 'SZ00' && !stock.isNew && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      sz00Loss +=
        stock.stockType == 'SZ00' && !stock.isNew && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      sz00Count += stock.stockType == 'SZ00' && !stock.isNew ? 1 : 0;

      sz300Profit +=
        stock.stockType == 'SZ300' && !stock.isNew && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      sz300Loss +=
        stock.stockType == 'SZ300' && !stock.isNew && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      sz300Count += stock.stockType == 'SZ300' && !stock.isNew ? 1 : 0;

      sh688Profit +=
        stock.stockType == 'SH688' && !stock.isNew && stock.offsetTotal > 0 ? stock.offsetTotal : 0;
      sh688Loss +=
        stock.stockType == 'SH688' && !stock.isNew && stock.offsetTotal < 0 ? stock.offsetTotal : 0;
      sh688Count += stock.stockType == 'SH688' && !stock.isNew ? 1 : 0;
    }

    analysis.push({
      type: '新股',
      count: isNewCount,
      profit: isNewProfit,
      loss: isNewLoss,
      netIncome: isNewProfit + isNewLoss,
    });

    analysis.push({
      type: '沪市（非新股）',
      count: sh60Count,
      profit: sh60Profit,
      loss: sh60Loss,
      netIncome: sh60Profit + sh60Loss,
    });

    analysis.push({
      type: '深市（非新股）',
      count: sz00Count,
      profit: sz00Profit,
      loss: sz00Loss,
      netIncome: sz00Profit + sz00Loss,
    });

    analysis.push({
      type: '创业板（非新股）',
      count: sz300Count,
      profit: sz300Profit,
      loss: sz300Loss,
      netIncome: sz300Profit + sz300Loss,
    });

    analysis.push({
      type: '科创板（非新股）',
      count: sh688Count,
      profit: sh688Profit,
      loss: sh688Loss,
      netIncome: sh688Profit + sh688Loss,
    });

    analysis.push({
      type: '分级基金',
      count: fundABCount,
      profit: fundABProfit,
      loss: fundABLoss,
      netIncome: fundABProfit + fundABLoss,
    });

    analysis.push({
      type: '场内基金',
      count: fundInCount,
      profit: fundInProfit,
      loss: fundInLoss,
      netIncome: fundInProfit + fundInLoss,
    });

    analysis.push({
      type: '可转债',
      count: convCount,
      profit: convProfit,
      loss: convLoss,
      netIncome: convProfit + convLoss,
    });

    analysis.push({
      type: '逆回购',
      count: 1,
      profit: stock.overall.incomeCash,
      loss: 0,
      netIncome: stock.overall.incomeCash,
    });

    setAnalysisList(analysis);
  };

  const analysisColumn: ColumnsType<any> = [
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

  return (
    <ProCard gutter={[0, 16]}>
      <Tabs defaultActiveKey="1">
        <TabPane tab="盈亏归因" key="1">
          <Table
            rowKey="code"
            columns={analysisColumn}
            dataSource={analysisList}
            bordered
            pagination={false}
          />
        </TabPane>
        <TabPane tab="费用明细" key="2">
          Content of Tab Pane 2
        </TabPane>
      </Tabs>
    </ProCard>
  );
};
