import { Table, Tooltip } from 'antd';
import React, { useState, useEffect, useCallback } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { colorFromValue } from '@/utils';

interface AnalysisModel {
  type: string;
  count: number;
  profit: number;
  loss: number;
  netIncome: number;
}

interface StockTypeStats {
  profit: number;
  loss: number;
  count: number;
}

export type AnalysisListProps = {
  data: API.Stock[];
  incomeCash?: number;
};

export const AnalysisList: React.FC<AnalysisListProps> = (props) => {
  const [analysisList, setAnalysisList] = useState<AnalysisModel[]>([]);
  const [totalProfit, setTotalProfit] = useState<number>(0);
  const [totalLoss, setTotalLoss] = useState<number>(0);

  /**
   * 初始化分析数据
   */
  const initializeAnalysis = useCallback((): void => {
    const analysis: AnalysisModel[] = [];

    // 初始化各类型统计数据
    const stats: Record<string, StockTypeStats> = {
      isNew: { profit: 0, loss: 0, count: 0 },
      fundAB: { profit: 0, loss: 0, count: 0 },
      fundIn: { profit: 0, loss: 0, count: 0 },
      conv: { profit: 0, loss: 0, count: 0 },
      sh60: { profit: 0, loss: 0, count: 0 },
      sz00: { profit: 0, loss: 0, count: 0 },
      sz300: { profit: 0, loss: 0, count: 0 },
      sh688: { profit: 0, loss: 0, count: 0 },
      bj: { profit: 0, loss: 0, count: 0 },
    };

    // 股票类型映射
    const typeMap: Record<string, keyof typeof stats> = {
      FUNDAB: 'fundAB',
      FUNDIN: 'fundIn',
      CONV: 'conv',
      SH60: 'sh60',
      SZ00: 'sz00',
      SZ300: 'sz300',
      SH688: 'sh688',
      BJ: 'bj',
    };

    // 统计各类型股票数据
    for (const stock of props.data) {
      const { stockType, isNew, offsetTotal } = stock;

      // 新股统计
      if (isNew) {
        if (offsetTotal > 0) stats.isNew.profit += offsetTotal;
        if (offsetTotal < 0) stats.isNew.loss += offsetTotal;
        stats.isNew.count++;
        continue;
      }

      // 根据股票类型统计（非新股）
      const statKey = typeMap[stockType];
      if (statKey) {
        if (offsetTotal > 0) stats[statKey].profit += offsetTotal;
        if (offsetTotal < 0) stats[statKey].loss += offsetTotal;
        stats[statKey].count++;
      }
    }

    // 计算总盈亏
    const totalProfitValue = Object.values(stats).reduce((sum, stat) => sum + stat.profit, 0);
    const totalLossValue = Object.values(stats).reduce((sum, stat) => sum + stat.loss, 0);

    setTotalProfit(totalProfitValue);
    setTotalLoss(totalLossValue);

    // 构建分析数据
    const createAnalysisItem = (
      type: string,
      statKey: keyof typeof stats,
    ): AnalysisModel => ({
      type,
      count: stats[statKey].count,
      profit: stats[statKey].profit,
      loss: stats[statKey].loss,
      netIncome: stats[statKey].profit + stats[statKey].loss,
    });

    analysis.push(createAnalysisItem('新股', 'isNew'));
    analysis.push(createAnalysisItem('沪市（非新股）', 'sh60'));
    analysis.push(createAnalysisItem('深市（非新股）', 'sz00'));
    analysis.push(createAnalysisItem('创业板（非新股）', 'sz300'));
    analysis.push(createAnalysisItem('科创板（非新股）', 'sh688'));
    analysis.push(createAnalysisItem('北交所（非新股）', 'bj'));
    analysis.push(createAnalysisItem('分级基金', 'fundAB'));
    analysis.push(createAnalysisItem('场内基金', 'fundIn'));
    analysis.push(createAnalysisItem('可转债', 'conv'));

    // 逆回购
    const incomeCashValue = props.incomeCash || 0;
    analysis.push({
      type: '逆回购',
      count: 1,
      profit: incomeCashValue,
      loss: 0,
      netIncome: incomeCashValue,
    });

    setAnalysisList(analysis);
  }, [props.data, props.incomeCash]);

  useEffect(() => {
    initializeAnalysis();
  }, [initializeAnalysis]);

  const columns: ColumnsType<AnalysisModel> = [
    {
      title: '类型',
      dataIndex: 'type',
      render: (item: string) => <strong>{item}</strong>,
    },
    {
      title: '数量',
      dataIndex: 'count',
    },
    {
      title: '获利',
      dataIndex: 'profit',
      render: (item: number) => {
        const ratio = `${((item / totalProfit) * 100).toFixed(2)}%`;
        return (
          <Tooltip title={ratio} color="red">
            <div style={{ color: 'red' }}>{item.toFixed(2)}</div>
          </Tooltip>
        );
      },
      sorter: (a, b) => a.profit - b.profit,
    },
    {
      title: '亏损',
      dataIndex: 'loss',
      render: (item: number) => {
        const ratio = `${((item / totalLoss) * 100).toFixed(2)}%`;
        return (
          <Tooltip title={ratio} color="green">
            <div style={{ color: 'green' }}>{item.toFixed(2)}</div>
          </Tooltip>
        );
      },
      sorter: (a, b) => a.loss - b.loss,
    },
    {
      title: '净收益',
      dataIndex: 'netIncome',
      render: (item: number) => (
        <div style={{ color: colorFromValue(item) }}>{item.toFixed(2)}</div>
      ),
      sorter: (a, b) => a.netIncome - b.netIncome,
    },
  ];

  return (
    <Table rowKey="type" columns={columns} dataSource={analysisList} bordered pagination={false} />
  );
};
