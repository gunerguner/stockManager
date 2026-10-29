import { Col, Row, Segmented, Statistic, Table, Tooltip } from 'antd';
import React, { useMemo, useState } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  buildAnalysisByIndustry,
  buildAnalysisByStockType,
  computeOverallProfitLoss,
  pinnedTailFor,
  sortAnalysisList,
  type AnalysisDimension,
  type AnalysisModel,
  type SortField,
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

type SortState = { field: SortField; order: 'ascend' | 'descend' };

const DIMENSION_OPTIONS: Array<{ value: AnalysisDimension; label: string }> = [
  { value: 'market', label: '按市场' },
  { value: 'industry', label: '按行业' },
];

const DEFAULT_SORT: SortState = { field: 'netIncome', order: 'descend' };

const toggleSort = (current: SortState, field: SortField): SortState => ({
  field,
  order: current.field === field && current.order === 'ascend' ? 'descend' : 'ascend',
});

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
        ? buildAnalysisByIndustry(data.stocks, incomeCash)
        : buildAnalysisByStockType(data.stocks, incomeCash),
    [data.stocks, incomeCash, dimension],
  );

  const pinnedTail = useMemo(() => pinnedTailFor(dimension), [dimension]);

  const displayList = useMemo(
    () => sortAnalysisList(analysisList, sortState.field, sortState.order, pinnedTail),
    [analysisList, sortState, pinnedTail],
  );

  const tailHeadKey = useMemo(() => {
    const pinned = new Set<string>(pinnedTail);
    const headIndex = displayList.findIndex((row) => pinned.has(row.key));
    if (headIndex <= 0) return undefined;
    return displayList[headIndex].key;
  }, [displayList, pinnedTail]);

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

  const columns: ColumnsType<AnalysisModel> = useMemo(() => {
    const amountCols: Array<{
      title: string;
      field: SortField;
      total?: number;
      color?: string;
    }> = [
      { title: '获利', field: 'profit', total: totalProfit, color: profitColor },
      { title: '亏损', field: 'loss', total: totalLoss, color: lossColor },
      { title: '净收益', field: 'netIncome' },
    ];

    return [
      {
        title: dimension === 'industry' ? '行业' : '类型',
        dataIndex: 'type',
        render: (text: string) => <strong>{text}</strong>,
      },
      {
        title: '数量',
        dataIndex: 'count',
      },
      ...amountCols.map(({ title, field, total, color }) => ({
        title,
        dataIndex: field,
        sorter: true,
        showSorterTooltip: false,
        sortOrder: sortState.field === field ? sortState.order : null,
        onHeaderCell: () => ({
          onClick: () => setSortState((prev) => toggleSort(prev, field)),
        }),
        render: (value: number) =>
          total != null && color ? (
            <Tooltip
              title={formatSharePercent(value, total)}
              color={color}
              styles={{ container: { color: '#fff' } }}
            >
              <AmountText value={value} />
            </Tooltip>
          ) : (
            <AmountText value={value} />
          ),
      })),
    ];
  }, [dimension, sortState, totalProfit, totalLoss, profitColor, lossColor]);

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
        {...getResponsiveTableProps(isMobile)}
        rowClassName={(record) => (record.key === tailHeadKey ? 'analysis-row-tail-head' : '')}
        onRow={(record) => ({
          onClick: () => handleRowClick(record),
          style: record.stocks.length > 0 ? { cursor: 'pointer' } : undefined,
        })}
      />
    </div>
  );
};
