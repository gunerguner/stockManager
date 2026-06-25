import { Col, Row, Statistic, Table, Tooltip } from 'antd';
import React, { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { buildAnalysisByStockType, HK_CATEGORY, type AnalysisModel } from './analysisStat';
import { getHeaderStatisticStyles } from '@/components/Common/statisticStyles';
import {
  formatSharePercent,
  MarketCurrency,
  toCnyByCurrency,
  toMarketCurrency,
} from '@/utils/format/stock';
import { renderAmount } from '@/utils/format/render';
import { useStockProfitModal } from './StockProfitModal';
import '@/components/Common/index.less';
import './index.less';

export type AnalysisListProps = {
  data: API.StockData;
  loading?: boolean;
};

export const AnalysisList: React.FC<AnalysisListProps> = ({
  data,
  loading = false,
}) => {
  const { incomeCash = 0, hkdCnyRate = 0 } = data.overall;
  const isMobile = useIsMobile();
  const { showStockProfit } = useStockProfitModal();
  const { profitColor, lossColor, colorFromValue } = useProfitLossColors();

  const { analysisList, totalProfit, totalLoss } = useMemo(
    () => buildAnalysisByStockType(data.stocks, { incomeCash, hkdCnyRate }),
    [data.stocks, incomeCash, hkdCnyRate],
  );

  const categoryCurrency = (record: AnalysisModel): MarketCurrency =>
    toMarketCurrency(record.type === HK_CATEGORY);

  const toCnyForPct = (record: AnalysisModel, value: number): number =>
    toCnyByCurrency(categoryCurrency(record), value, hkdCnyRate || 1);

  const renderCategoryAmount = (value: number, color: string, record: AnalysisModel) =>
    renderAmount(value, { currency: categoryCurrency(record), color });

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
            title={formatSharePercent(toCnyForPct(record, value), totalProfit)}
            color={profitColor}
            styles={{ container: { color: '#fff' } }}
          >
            {renderCategoryAmount(value, profitColor, record)}
          </Tooltip>
        ),
      },
      {
        title: '亏损',
        dataIndex: 'loss',
        sorter: (a, b) => a.loss - b.loss,
        render: (value: number, record: AnalysisModel) => (
          <Tooltip
            title={formatSharePercent(toCnyForPct(record, value), totalLoss)}
            color={lossColor}
            styles={{ container: { color: '#fff' } }}
          >
            {renderCategoryAmount(value, lossColor, record)}
          </Tooltip>
        ),
      },
      {
        title: '净收益',
        dataIndex: 'netIncome',
        sorter: (a, b) => a.netIncome - b.netIncome,
        render: (value: number, record: AnalysisModel) =>
          renderCategoryAmount(value, colorFromValue(value) ?? '', record),
      },
    ],
    [totalProfit, totalLoss, hkdCnyRate, profitColor, lossColor, colorFromValue],
  );

  return (
    <div className="table-list-wrapper analysis-list-wrapper">
      <Row gutter={[16, 16]} className="table-list-header">
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="总获利"
            value={totalProfit}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, profitColor)}
          />
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Statistic
            title="总亏损"
            value={totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, lossColor)}
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
        loading={loading}
        pagination={false}
        {...getResponsiveTableProps(isMobile)}
        onRow={(record) => ({
          onClick: () => handleRowClick(record),
          style: record.stocks.length > 0 ? { cursor: 'pointer' } : undefined,
        })}
      />
    </div>
  );
};
