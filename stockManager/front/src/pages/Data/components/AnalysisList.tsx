import { Col, Row, Statistic, Table, Tooltip } from 'antd';
import React, { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { colorFromValue, renderAmount as renderAmountTool } from '@/utils/renderTool';
import { useStockProfitModal } from '@/components/Common/StockProfitModal';
import './index.less';

// ==================== 类型定义 ====================

interface StockDetail {
  code: string;
  name: string;
  profit: number;
  loss: number;
  netIncome: number;
}

interface AnalysisModel {
  type: string;
  count: number;
  profit: number;
  loss: number;
  netIncome: number;
  stocks: StockDetail[];
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

// ==================== 组件 ====================

export const AnalysisList: React.FC<AnalysisListProps> = ({ data, incomeCash = 0 }) => {
  const isMobile = useIsMobile();
  const { showStockProfit } = useStockProfitModal();

  /** 计算分析数据 */
  const { analysisList, totalProfit, totalLoss } = useMemo(() => {
    // 初始化统计对象
    const stats = new Map<string, AnalysisModel>(
      STOCK_TYPE_CONFIGS.map(([key, label]) => [
        key,
        { type: label, count: 0, profit: 0, loss: 0, netIncome: 0, stocks: [] },
      ]),
    );

    // 统计各类型股票数据
    for (const stock of data) {
      const { stockType, isNew, offsetTotal } = stock;
      const key = isNew ? 'isNew' : API_TYPE_MAP.get(stockType);
      const stat = key ? stats.get(key) : undefined;
      
      if (stat) {
        const profit = offsetTotal > 0 ? offsetTotal : 0;
        const loss = offsetTotal < 0 ? offsetTotal : 0;
        
        stat.profit += profit;
        stat.loss += loss;
        stat.count++;
        stat.netIncome += offsetTotal;
        stat.stocks.push({
          code: stock.code,
          name: stock.name,
          profit,
          loss,
          netIncome: offsetTotal,
        });
      }
    }

    // 构建分析数据并计算总盈亏
    const analysisList = [...stats.values()];
    const totalProfit = analysisList.reduce((sum, s) => sum + s.profit, 0);
    const totalLoss = analysisList.reduce((sum, s) => sum + s.loss, 0);

    // 添加逆回购（如果有）
    if (incomeCash > 0) {
      analysisList.push({
        type: '逆回购',
        count: 1,
        profit: incomeCash,
        loss: 0,
        netIncome: incomeCash,
        stocks: [],
      });
    }

    return { analysisList, totalProfit, totalLoss };
  }, [data, incomeCash]);

  /** 渲染金额（复用通用渲染工具） */
  const renderAmount = (value: number, color: string) => renderAmountTool(value, color);

  /** 处理行点击事件 */
  const handleRowClick = (record: AnalysisModel) => {
    if (record.stocks.length === 0) return;
    
    showStockProfit({
      data: record.stocks,
      categoryName: record.type,
      profit: record.profit,
      loss: record.loss,
      netIncome: record.netIncome,
    });
  };

  /** 主表格列配置 */
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
            {renderAmount(value, 'red')}
          </Tooltip>
        ),
      },
      {
        title: '亏损',
        dataIndex: 'loss',
        sorter: (a, b) => a.loss - b.loss,
        render: (value: number) => (
          <Tooltip title={`${((value / totalLoss) * 100).toFixed(2)}%`} color="green">
            {renderAmount(value, 'green')}
          </Tooltip>
        ),
      },
      {
        title: '净收益',
        dataIndex: 'netIncome',
        sorter: (a, b) => a.netIncome - b.netIncome,
        render: (value: number) => renderAmount(value, colorFromValue(value)),
      },
    ],
    [totalProfit, totalLoss],
  );

  /** 头部 Statistic 样式（使用 css-in-js） */
  const getHeaderStatisticStyles = (color?: string) => ({
    title: {
      fontSize: isMobile ? 12 : '',
      marginBottom: 4,
    },
    content: {
      fontSize: isMobile ? 18 : '',
      ...(color ? { color } : {}),
    },
  });

  return (
    <div className="analysis-list-wrapper">
      <Row gutter={[16, 16]} className="analysis-list-header">
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="总获利"
            value={totalProfit}
            precision={2}
            styles={getHeaderStatisticStyles('red')}
          />
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="总亏损"
            value={totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles('green')}
          />
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="净收益"
            value={totalProfit + totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles(colorFromValue(totalProfit + totalLoss))}
          />
        </Col>
      </Row>
      <div className="analysis-list-table-container">
        <Table
          rowKey="type"
          columns={columns}
          dataSource={analysisList}
          bordered
          pagination={false}
          scroll={isMobile ? { x: 'max-content' } : undefined}
          size={isMobile ? 'small' : 'middle'}
          tableLayout="auto"
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            style: record.stocks.length > 0 ? { cursor: 'pointer' } : undefined,
          })}
        />
      </div>
    </div>
  );
};
