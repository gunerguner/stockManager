import { Table, Tooltip } from 'antd';
import { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  formatAmount,
  formatDecimalRatio,
  formatMarketPrice,
  hkNative,
  isHkCode,
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
    return [
      {
        title: '名称',
        dataIndex: 'name',
        width: isMobile ? 100 : undefined,
        fixed: 'left',
        render: (_, r) => <HoldingStatus {...r} nameClassName="stock-name-link" />,
      },
      {
        title: '现价',
        dataIndex: 'priceNow',
        className: 'cell-number',
        width: isMobile ? 70 : undefined,
        render: (v, r) => <div className="cell-number">{formatMarketPrice(v, r.code)}</div>,
      },
      {
        title: '当日涨跌',
        dataIndex: 'offsetTodayRatio',
        className: 'cell-number',
        width: isMobile ? 90 : undefined,
        render: (_, r) => {
          const cell = renderDailyChange(
            r.offsetToday,
            r.offsetTodayRatio,
            r.code,
            colorFromValue,
          );
          const cny = formatAmount(r.totalOffsetToday);
          const title = isHkCode(r.code)
            ? `${cny}/${formatAmount(hkNative.offsetToday(r), { currency: 'hkd' })}`
            : cny;
          return (
            <Tooltip
              title={title}
              color={colorFromValue(r.totalOffsetToday)}
              styles={{ container: { color: '#fff' } }}
            >
              {cell}
            </Tooltip>
          );
        },
      },
      {
        title: '市值',
        dataIndex: 'totalValue',
        className: 'cell-number',
        width: isMobile ? 80 : undefined,
        defaultSortOrder: 'descend',
        sorter: (a, b) => a.totalValue - b.totalValue,
        render: (_, r) => {
          const cell = <div className="cell-number">{formatAmount(r.totalValue)}</div>;
          if (!isHkCode(r.code)) return cell;
          return (
            <Tooltip title={formatAmount(hkNative.totalValue(r), { currency: 'hkd' })}>{cell}</Tooltip>
          );
        },
      },
      {
        title: '持仓',
        dataIndex: 'holdCount',
        className: 'cell-number',
        width: isMobile ? 60 : undefined,
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
        width: isMobile ? 120 : undefined,
        render: (_, r) => (
          <div className="cell-number">
            {`${formatMarketPrice(r.overallCost, r.code)}/${formatMarketPrice(r.holdCost, r.code)}`}
          </div>
        ),
      },
      {
        title: '浮动盈亏',
        dataIndex: 'offsetCurrent',
        className: 'cell-number',
        width: isMobile ? 80 : undefined,
        sorter: (a, b) => a.offsetCurrent - b.offsetCurrent,
        render: (_, r) => {
          const cell = (
            <div className="cell-number">
              {renderAmount(r.offsetCurrent, {
                profitLossColors: { profitColor, lossColor },
              })}
            </div>
          );
          if (!isHkCode(r.code)) return cell;
          const hkd = hkNative.offsetCurrent(r);
          return (
            <Tooltip
              title={formatAmount(hkd, { currency: 'hkd' })}
              color={colorFromValue(hkd)}
              styles={{ container: { color: '#fff' } }}
            >
              {cell}
            </Tooltip>
          );
        },
      },
      {
        title: '累计盈亏',
        dataIndex: 'offsetTotal',
        className: 'cell-number',
        width: isMobile ? 110 : undefined,
        sorter: (a, b) => a.offsetTotal - b.offsetTotal,
        render: (_, r) => {
          const cell = (
            <div className="cell-number" style={{ color: colorFromValue(r.offsetTotal) }}>
              {`${formatAmount(r.offsetTotal)} (${formatDecimalRatio(r.moneyWeightedReturn)})`}
            </div>
          );
          if (!isHkCode(r.code)) return cell;
          const hkd = hkNative.offsetTotal(r);
          if (hkd == null) return cell;
          return (
            <Tooltip
              title={formatAmount(hkd, { currency: 'hkd' })}
              color={colorFromValue(hkd)}
              styles={{ container: { color: '#fff' } }}
            >
              {cell}
            </Tooltip>
          );
        },
      },
    ];
  }, [isMobile, profitColor, lossColor, colorFromValue]);

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
