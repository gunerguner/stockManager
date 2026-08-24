import { Col, Row, Segmented, Statistic, Table, Tooltip } from 'antd';
import React, { useMemo, useState } from 'react';
import type { ColumnsType, TableProps } from 'antd/lib/table';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  buildAnalysisByIndustry,
  buildAnalysisByStockType,
  computeOverallProfitLoss,
  sortAnalysisList,
  type AnalysisModel,
} from './analysisStat';
import { getHeaderStatisticStyles } from '@/components/Common/statisticStyles';
import { formatSharePercent } from '@/utils/format/stock';
import { AmountText } from '@/utils/format/render';
import { useStockProfitModal } from './StockProfitModal';
import '@/components/Common/index.less';
import './index.less';

export type AnalysisListProps = {
  data: API.StockData;
  loading?: boolean;
};

type AnalysisDimension = 'market' | 'industry';
type SortField = 'profit' | 'loss' | 'netIncome';
type SortState = { field: SortField; order: 'ascend' | 'descend' };

const DIMENSION_OPTIONS: Array<{ value: AnalysisDimension; label: string }> = [
  { value: 'market', label: '按市场' },
  { value: 'industry', label: '按行业' },
];

const DEFAULT_SORT: SortState = { field: 'netIncome', order: 'descend' };

const toSingleSorter = (
  sorter: Parameters<NonNullable<TableProps<AnalysisModel>['onChange']>>[2],
) => (Array.isArray(sorter) ? sorter[0] : sorter);

export const AnalysisList: React.FC<AnalysisListProps> = ({
  data,
  loading = false,
}) => {
  const { incomeCash = 0 } = data.overall;
  const isMobile = useIsMobile();
  const { showStockProfit } = useStockProfitModal();
  const { profitColor, lossColor, colorFromValue } = useProfitLossColors();
  const [dimension, setDimension] = useState<AnalysisDimension>('market');
  const [sortState, setSortState] = useState<SortState>(DEFAULT_SORT);

  const { totalProfit, totalLoss } = useMemo(
    () => computeOverallProfitLoss(data.stocks, incomeCash),
    [data.stocks, incomeCash],
  );

  const analysisList = useMemo(
    () =>
      dimension === 'industry'
        ? buildAnalysisByIndustry(data.stocks, { incomeCash })
        : buildAnalysisByStockType(data.stocks, { incomeCash }),
    [data.stocks, incomeCash, dimension],
  );

  const displayList = useMemo(
    () => sortAnalysisList(analysisList, sortState.field, sortState.order),
    [analysisList, sortState],
  );

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

  const handleTableChange: TableProps<AnalysisModel>['onChange'] = (_pagination, _filters, sorter) => {
    const current = toSingleSorter(sorter);
    const field = current?.field;
    if (
      (field === 'profit' || field === 'loss' || field === 'netIncome') &&
      (current.order === 'ascend' || current.order === 'descend')
    ) {
      setSortState({ field, order: current.order });
      return;
    }
    setSortState(DEFAULT_SORT);
  };

  const columns: ColumnsType<AnalysisModel> = useMemo(
    () => [
      {
        title: dimension === 'industry' ? '行业' : '类型',
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
        sorter: true,
        sortOrder: sortState.field === 'profit' ? sortState.order : undefined,
        render: (value: number) => (
          <Tooltip
            title={formatSharePercent(value, totalProfit)}
            color={profitColor}
            styles={{ container: { color: '#fff' } }}
          >
            <AmountText value={value} />
          </Tooltip>
        ),
      },
      {
        title: '亏损',
        dataIndex: 'loss',
        sorter: true,
        sortOrder: sortState.field === 'loss' ? sortState.order : undefined,
        render: (value: number) => (
          <Tooltip
            title={formatSharePercent(value, totalLoss)}
            color={lossColor}
            styles={{ container: { color: '#fff' } }}
          >
            <AmountText value={value} />
          </Tooltip>
        ),
      },
      {
        title: '净收益',
        dataIndex: 'netIncome',
        sorter: true,
        sortOrder: sortState.field === 'netIncome' ? sortState.order : undefined,
        render: (value: number) => <AmountText value={value} />,
      },
    ],
    [dimension, sortState, totalProfit, totalLoss, profitColor, lossColor],
  );

  return (
    <div className="table-list-wrapper analysis-list-wrapper">
      <Row gutter={[isMobile ? 8 : 16, 8]} className="table-list-header">
        <Col span={isMobile ? 8 : 6}>
          <Statistic
            title="总获利"
            value={totalProfit}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, profitColor)}
          />
        </Col>
        <Col span={isMobile ? 8 : 6}>
          <Statistic
            title="总亏损"
            value={totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, lossColor)}
          />
        </Col>
        <Col span={isMobile ? 8 : 6}>
          <Statistic
            title="净收益"
            value={totalProfit + totalLoss}
            precision={2}
            styles={getHeaderStatisticStyles(isMobile, colorFromValue(totalProfit + totalLoss))}
          />
        </Col>
      </Row>
      <div className="analysis-dimension-switch">
        <Segmented
          value={dimension}
          onChange={(value) => setDimension(value as AnalysisDimension)}
          options={DIMENSION_OPTIONS}
          size={isMobile ? 'small' : 'middle'}
        />
      </div>
      <Table
        rowKey="key"
        columns={columns}
        dataSource={displayList}
        loading={loading}
        pagination={false}
        onChange={handleTableChange}
        {...getResponsiveTableProps(isMobile)}
        onRow={(record) => ({
          onClick: () => handleRowClick(record),
          style: record.stocks.length > 0 ? { cursor: 'pointer' } : undefined,
        })}
      />
    </div>
  );
};
