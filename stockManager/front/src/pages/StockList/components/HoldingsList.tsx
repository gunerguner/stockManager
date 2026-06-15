import { Table, Tooltip } from 'antd';
import { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  formatAmount,
  formatDecimalRatio,
  formatMarketPrice,
  formatSharePercent,
  toCnyAmount,
} from '@/utils/format/stock';
import { HoldingStatus } from '@/components/Common/HoldingStatus';
import { renderAmount, renderDailyChange } from '@/utils/format/render';
import { useTradeDetailModal } from '@/components/Common/modal/TradeDetailModal';
import './index.less';

type HoldingsListProps = {
  data: API.StockData;
  operations: Record<string, API.Operation[]>;
  showAll: boolean;
  showConv: boolean;
  loading?: boolean;
};

export const HoldingsList: React.FC<HoldingsListProps> = ({
  data,
  operations,
  showAll,
  showConv,
  loading = false,
}) => {
  const isMobile = useIsMobile();
  const { showTradeDetail } = useTradeDetailModal();
  const { profitColor, lossColor, colorFromValue } = useProfitLossColors();

  const handleRowClick = (record: API.Stock) => {
    showTradeDetail({
      data: [{ stock: record, operations: operations[record.code] || [] }],
      displayType: 'stockInfo',
    });
  };

  const filteredData = useMemo(() => {
    return data.stocks.filter(
      (record) =>
        !((record.totalValue < 0.1 && !showAll) || (record.stockType === 'CONV' && !showConv)),
    );
  }, [data.stocks, showAll, showConv]);

  const columns: ColumnsType<API.Stock> = useMemo(() => {
    const hkdCnyRate = data.overall.hkdCnyRate ?? 0;

    return [
      {
        title: '名称',
        dataIndex: 'name',
        fixed: isMobile ? false : 'left',
        render: (_, r) => <HoldingStatus {...r} nameClassName="stock-name-link" />,
      },
      {
        title: '现价',
        dataIndex: 'priceNow',
        className: 'cell-number',
        render: (v, r) => <div className="cell-number">{formatMarketPrice(v, r.code)}</div>,
      },
      {
        title: '涨跌',
        dataIndex: 'offsetTodayRatio',
        className: 'cell-number',
        render: (_, r) =>
          renderDailyChange(r.offsetToday, r.offsetTodayRatio, r.code, colorFromValue),
      },
      {
        title: '市值',
        dataIndex: 'totalValue',
        className: 'cell-number',
        defaultSortOrder: 'descend',
        sorter: (a, b) => a.totalValue - b.totalValue,
        render: (_, r) => {
          const valueCny = toCnyAmount(r.code, r.totalValue, hkdCnyRate);
          const total = data.overall.totalValue;
          const percentage = formatSharePercent(valueCny, total);
          return (
            <Tooltip title={percentage}>
              <div className="cell-number">{formatAmount(r.totalValue, { code: r.code })}</div>
            </Tooltip>
          );
        },
      },
      {
        title: '持仓',
        dataIndex: 'holdCount',
        className: 'cell-number',
        render: (_, r) => (
          <Tooltip title={`持股 ${r.holdingDuration} 天`}>
            <div className="cell-number">{r.holdCount}</div>
          </Tooltip>
        ),
      },
      {
        title: '摊薄/持仓成本',
        dataIndex: 'overallCost',
        className: 'cell-number',
        render: (_, r) => (
          <div className="cell-number">
            {`${formatAmount(r.overallCost, { code: r.code })}/${formatAmount(r.holdCost, { code: r.code })}`}
          </div>
        ),
      },
      {
        title: '浮动盈亏',
        dataIndex: 'offsetCurrent',
        className: 'cell-number',
        sorter: (a, b) =>
          toCnyAmount(a.code, a.offsetCurrent, hkdCnyRate) -
          toCnyAmount(b.code, b.offsetCurrent, hkdCnyRate),
        render: (_, r) => {
          const todayTotal = r.offsetToday * r.holdCount;
          return (
            <Tooltip
              title={formatAmount(todayTotal, { code: r.code })}
              color={colorFromValue(todayTotal)}
              styles={{ container: { color: '#fff' } }}
            >
              <div className="cell-number">
                {renderAmount(r.offsetCurrent, {
                  code: r.code,
                  profitLossColors: { profitColor, lossColor },
                })}
              </div>
            </Tooltip>
          );
        },
      },
      {
        title: '累计盈亏',
        dataIndex: 'offsetTotal',
        className: 'cell-number',
        sorter: (a, b) =>
          toCnyAmount(a.code, a.offsetTotal, hkdCnyRate) -
          toCnyAmount(b.code, b.offsetTotal, hkdCnyRate),
        render: (_, r) => (
          <div className="cell-number" style={{ color: colorFromValue(r.offsetTotal) }}>
            {`${formatAmount(r.offsetTotal, { code: r.code })} (${formatDecimalRatio(r.moneyWeightedReturn)})`}
          </div>
        ),
      },
    ];
  }, [
    isMobile,
    data.overall.totalValue,
    data.overall.hkdCnyRate,
    profitColor,
    lossColor,
    colorFromValue,
  ]);

  return (
    <div className="holdings-list-wrapper">
      <Table
        rowKey="code"
        columns={columns}
        dataSource={filteredData}
        loading={loading}
        pagination={false}
        onRow={(r) => ({ onClick: () => handleRowClick(r), style: { cursor: 'pointer' } })}
        {...getResponsiveTableProps(isMobile)}
      />
    </div>
  );
};
