import { Col, Row, Statistic, Table, Tooltip } from 'antd';
import React, { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { colorFromValue, toCnyAmount } from '@/utils/format/stock';
import { renderAmount as renderAmountTool } from '@/utils/format/render';
import { getHeaderStatisticStyles } from '@/utils/statisticStyles';
import { useStockProfitModal } from '@/components/Common/StockProfitModal';
import './index.less';

// ==================== 类型定义 ====================

interface StockDetail {
  code: string;
  name: string;
  profit: number;
  loss: number;
  netIncome: number;
  holdCount?: number;
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
  hkdCnyRate?: number;
};

const HK_CATEGORY = '港股通';
const HK_AMOUNT_CODE = 'hk00000';

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
  ['hk', HK_CATEGORY, 'HK'],
];

/** API 股票类型 -> 内部键 映射表 */
const API_TYPE_MAP = new Map(
  STOCK_TYPE_CONFIGS
    .filter(([, , apiType]) => apiType)
    .map(([key, , apiType]) => [apiType!, key]),
);

// ==================== 组件 ====================

export const AnalysisList: React.FC<AnalysisListProps> = ({
  data,
  incomeCash = 0,
  hkdCnyRate = 0,
}) => {
  const isMobile = useIsMobile();
  const { showStockProfit } = useStockProfitModal();

  /** 计算分析数据 */
  const { analysisList, totalProfit, totalLoss } = useMemo(() => {
    const stats = new Map<string, AnalysisModel>(
      STOCK_TYPE_CONFIGS.map(([key, label]) => [
        key,
        { type: label, count: 0, profit: 0, loss: 0, netIncome: 0, stocks: [] },
      ]),
    );

    let totalProfitCny = 0;
    let totalLossCny = 0;

    for (const stock of data) {
      const { stockType, isNew, offsetTotal, code } = stock;
      const key = isNew ? 'isNew' : API_TYPE_MAP.get(stockType);
      const stat = key ? stats.get(key) : undefined;

      const cnyOffset = toCnyAmount(code, offsetTotal, hkdCnyRate);
      if (cnyOffset > 0) totalProfitCny += cnyOffset;
      else if (cnyOffset < 0) totalLossCny += cnyOffset;

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
          holdCount: stock.holdCount,
        });
      }
    }

    const analysisList = [...stats.values()];

    if (incomeCash > 0) {
      analysisList.push({
        type: '逆回购',
        count: 1,
        profit: incomeCash,
        loss: 0,
        netIncome: incomeCash,
        stocks: [],
      });
      totalProfitCny += incomeCash;
    }

    return {
      analysisList,
      totalProfit: totalProfitCny,
      totalLoss: totalLossCny,
    };
  }, [data, incomeCash, hkdCnyRate]);

  const toCnyForPct = (record: AnalysisModel, value: number): number =>
    record.type === HK_CATEGORY ? value * (hkdCnyRate || 1) : value;

  const renderCategoryAmount = (value: number, color: string, record: AnalysisModel) =>
    renderAmountTool(value, color, 2, record.type === HK_CATEGORY ? HK_AMOUNT_CODE : undefined);

  const handleRowClick = (record: AnalysisModel) => {
    if (record.stocks.length === 0) return;

    showStockProfit({
      data: record.stocks,
      categoryName: record.type,
      profit: record.profit,
      loss: record.loss,
      netIncome: record.netIncome,
      isHkCategory: record.type === HK_CATEGORY,
    });
  };

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
        render: (value: number, record: AnalysisModel) => (
          <Tooltip
            title={`${totalProfit ? ((toCnyForPct(record, value) / totalProfit) * 100).toFixed(2) : '0.00'}%`}
            color="red"
          >
            {renderCategoryAmount(value, 'red', record)}
          </Tooltip>
        ),
      },
      {
        title: '亏损',
        dataIndex: 'loss',
        sorter: (a, b) => a.loss - b.loss,
        render: (value: number, record: AnalysisModel) => (
          <Tooltip
            title={`${totalLoss ? ((toCnyForPct(record, value) / totalLoss) * 100).toFixed(2) : '0.00'}%`}
            color="green"
          >
            {renderCategoryAmount(value, 'green', record)}
          </Tooltip>
        ),
      },
      {
        title: '净收益',
        dataIndex: 'netIncome',
        sorter: (a, b) => a.netIncome - b.netIncome,
        render: (value: number, record: AnalysisModel) =>
          renderCategoryAmount(value, colorFromValue(value), record),
      },
    ],
    [totalProfit, totalLoss, hkdCnyRate],
  );

  return (
    <div className="table-list-wrapper analysis-list-wrapper">
      <Row gutter={[16, 16]} className="table-list-header">
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="总获利"
            value={totalProfit}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, 'red')}
          />
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="总亏损"
            value={totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, 'green')}
          />
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="净收益"
            value={totalProfit + totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, colorFromValue(totalProfit + totalLoss))}
          />
        </Col>
      </Row>
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
  );
};
