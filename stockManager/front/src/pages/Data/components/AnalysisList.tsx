import { Table, Tooltip } from 'antd';
import React, { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { colorFromValue } from '@/utils';
import './index.less';

// ==================== 类型定义 ====================

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

// ==================== 配置 ====================

/** 股票类型配置：[内部键, 显示名称, API类型(可选)] */
const STOCK_TYPE_CONFIGS: Array<[string, string, string?]> = [
  ['isNew', '新股'],
  ['sh60', '沪市（非新股）', 'SH60'],
  ['sz00', '深市（非新股）', 'SZ00'],
  ['sz300', '创业板（非新股）', 'SZ300'],
  ['sh688', '科创板（非新股）', 'SH688'],
  ['bj', '北交所（非新股）', 'BJ'],
  ['fundAB', '分级基金', 'FUNDAB'],
  ['fundIn', '场内基金', 'FUNDIN'],
  ['conv', '可转债', 'CONV'],
];

/** API 股票类型 -> 内部键 映射表 */
const API_TYPE_MAP = new Map(
  STOCK_TYPE_CONFIGS
    .filter(([, , apiType]) => apiType)
    .map(([key, , apiType]) => [apiType!, key]),
);

// ==================== 工具函数 ====================

/** 创建空的统计对象 */
const createEmptyStats = (): StockTypeStats => ({ profit: 0, loss: 0, count: 0 });

/** 累加统计数据 */
const accumulateStats = (stats: StockTypeStats, offsetTotal: number): void => {
  if (offsetTotal > 0) stats.profit += offsetTotal;
  if (offsetTotal < 0) stats.loss += offsetTotal;
  stats.count++;
};

// ==================== 组件 ====================

export const AnalysisList: React.FC<AnalysisListProps> = ({ data, incomeCash = 0 }) => {
  const isMobile = useIsMobile();

  /** 计算分析数据 */
  const { analysisList, totalProfit, totalLoss } = useMemo(() => {
    // 初始化统计对象
    const stats = new Map<string, StockTypeStats>(
      STOCK_TYPE_CONFIGS.map(([key]) => [key, createEmptyStats()]),
    );

    // 统计各类型股票数据
    for (const { stockType, isNew, offsetTotal } of data) {
      const key = isNew ? 'isNew' : API_TYPE_MAP.get(stockType);
      const stat = key ? stats.get(key) : undefined;
      if (stat) accumulateStats(stat, offsetTotal);
    }

    // 计算总盈亏
    const allStats = [...stats.values()];
    const totalProfitValue = allStats.reduce((sum, s) => sum + s.profit, 0);
    const totalLossValue = allStats.reduce((sum, s) => sum + s.loss, 0);

    // 构建分析数据
    const analysis: AnalysisModel[] = STOCK_TYPE_CONFIGS.map(([key, label]) => {
      const stat = stats.get(key)!;
      return {
        type: label,
        count: stat.count,
        profit: stat.profit,
        loss: stat.loss,
        netIncome: stat.profit + stat.loss,
      };
    });

    // 添加逆回购（如果有）
    if (incomeCash > 0) {
      analysis.push({
        type: '逆回购',
        count: 1,
        profit: incomeCash,
        loss: 0,
        netIncome: incomeCash,
      });
    }

    return { analysisList: analysis, totalProfit: totalProfitValue, totalLoss: totalLossValue };
  }, [data, incomeCash]);

  /** 表格列配置 */
  const columns: ColumnsType<AnalysisModel> = useMemo(
    () => [
      {
        title: '类型',
        dataIndex: 'type',
        render: (text: string) => <strong>{text}</strong>,
      },
      {
        title: '数量',
        dataIndex: 'count',
      },
      {
        title: '获利',
        dataIndex: 'profit',
        sorter: (a, b) => a.profit - b.profit,
        render: (value: number) => (
          <Tooltip title={`${((value / totalProfit) * 100).toFixed(2)}%`} color="red">
            <span style={{ color: 'red' }}>{value.toFixed(2)}</span>
          </Tooltip>
        ),
      },
      {
        title: '亏损',
        dataIndex: 'loss',
        sorter: (a, b) => a.loss - b.loss,
        render: (value: number) => (
          <Tooltip title={`${((value / totalLoss) * 100).toFixed(2)}%`} color="green">
            <span style={{ color: 'green' }}>{value.toFixed(2)}</span>
          </Tooltip>
        ),
      },
      {
        title: '净收益',
        dataIndex: 'netIncome',
        sorter: (a, b) => a.netIncome - b.netIncome,
        render: (value: number) => (
          <span style={{ color: colorFromValue(value) }}>{value.toFixed(2)}</span>
        ),
      },
    ],
    [totalProfit, totalLoss],
  );

  return (
    <div className="analysis-list-wrapper">
      <Table
        rowKey="type"
        columns={columns}
        dataSource={analysisList}
        bordered
        pagination={false}
        scroll={isMobile ? { x: 'max-content' } : undefined}
        size={isMobile ? 'small' : 'middle'}
        tableLayout="auto"
      />
    </div>
  );
};
