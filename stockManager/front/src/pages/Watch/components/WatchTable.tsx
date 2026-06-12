import { Descriptions, Table, Tooltip, theme } from 'antd';
import { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useCommonModal } from '@/components/Common/useCommonModal';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import {
  formatMarketPrice,
  formatPercent,
  isHkCode,
  toXueqiuStockUrl,
} from '@/utils/format/stock';
import { renderHoldingStatus } from '@/utils/format/render';
import '@/components/Common/index.less';

type WatchTableProps = {
  data: API.WatchItem[];
  loading?: boolean;
};

const isBuyPointTriggered = (priceNow: number | null, point: number | null): boolean =>
  priceNow != null && point != null && point > 0 && priceNow <= point * 1.05;

const isTrendPointTriggered = (priceNow: number | null, point: number | null): boolean =>
  priceNow != null && point != null && point > 0 && priceNow > point;

const formatRatio = (value: number | null): string =>
  value != null && !Number.isNaN(value) ? value.toFixed(2) : '—';

const calcRoeFromPbPe = (pb: number | null, pe: number | null): number | null => {
  if (pb == null || pe == null || Number.isNaN(pb) || Number.isNaN(pe) || pe === 0) {
    return null;
  }
  return (pb / pe) * 100;
};

const renderMultilineText = (text: string) => {
  if (!text) return '—';
  return <span style={{ whiteSpace: 'pre-wrap' }}>{text}</span>;
};

export const WatchTable: React.FC<WatchTableProps> = ({ data, loading = false }) => {
  const isMobile = useIsMobile();
  const { showModal } = useCommonModal();
  const { profitColor, lossColor, colorFromValue, highlightStyle } = useProfitLossColors();
  const { token } = theme.useToken();

  const renderHistHighDropPct = (histHigh: number | null, priceNow: number | null): React.ReactNode => {
    if (priceNow == null || histHigh == null || histHigh <= 0) return '—';
    const dropPct = ((priceNow - histHigh) / histHigh) * 100;
    return (
      <span style={{ color: colorFromValue(dropPct) }}>{formatPercent(dropPct)}</span>
    );
  };

  const renderBuyPoint = (val: number | null, record: API.WatchItem) => {
    if (val == null || val <= 0) {
      return <span style={{ color: token.colorTextDisabled }}>—</span>;
    }
    const hit = isBuyPointTriggered(record.priceNow, val);
    return (
      <span style={hit ? highlightStyle : undefined}>{formatMarketPrice(val, record.code)}</span>
    );
  };

  const renderTrendPoint = (val: number | null, record: API.WatchItem) => {
    if (val == null || val <= 0) {
      return <span style={{ color: token.colorTextDisabled }}>—</span>;
    }
    const hit = isTrendPointTriggered(record.priceNow, val);
    return (
      <span style={hit ? highlightStyle : undefined}>{formatMarketPrice(val, record.code)}</span>
    );
  };

  const handleRowClick = (record: API.WatchItem) => {
    showModal({
      title: `${record.name}（${record.code}）`,
      width: 768,
      content: (
        <Descriptions column={1} size="small" className="watch-detail-descriptions">
          <Descriptions.Item label="风险">{renderMultilineText(record.risk)}</Descriptions.Item>
          <Descriptions.Item label="机会">{renderMultilineText(record.opportunity)}</Descriptions.Item>
          <Descriptions.Item label="左侧点">
            {record.leftPoint != null ? formatMarketPrice(record.leftPoint, record.code) : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="趋势点">
            {record.trendPoint != null ? formatMarketPrice(record.trendPoint, record.code) : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="血筹点">
            {record.bloodPoint != null ? formatMarketPrice(record.bloodPoint, record.code) : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="现价">
            {record.priceNow != null ? formatMarketPrice(record.priceNow, record.code) : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="6年内最高">
            {record.histHigh != null ? formatMarketPrice(record.histHigh, record.code) : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="PB">{formatRatio(record.pb)}</Descriptions.Item>
          <Descriptions.Item label="PE(TTM)">{formatRatio(record.pe)}</Descriptions.Item>
          <Descriptions.Item label="ROE">
            {formatPercent(calcRoeFromPbPe(record.pb, record.pe))}
          </Descriptions.Item>
        </Descriptions>
      ),
    });
  };

  const columns: ColumnsType<API.WatchItem> = useMemo(
    () => [
      {
        title: '名称',
        dataIndex: 'name',
        fixed: isMobile ? false : 'left',
        render: (_, record) =>
          renderHoldingStatus({
            name: record.name,
            code: record.code,
            link: toXueqiuStockUrl(record.code),
            isProfit: false,
            holding: record.holding,
            isHk: isHkCode(record.code),
            nameClassName: 'stock-name-link',
            profitColor,
            lossColor,
          }),
      },
      {
        title: '现价',
        dataIndex: 'priceNow',
        render: (value, record) =>
          value != null ? formatMarketPrice(value, record.code) : '—',
      },
      {
        title: '涨跌',
        dataIndex: 'offsetTodayRatio',
        render: (_, record) =>
          record.priceNow != null ? (
            <div style={{ color: colorFromValue(record.offsetToday) }}>
              {`${formatMarketPrice(record.offsetToday, record.code)} (${formatPercent(record.offsetTodayRatio * 100)})`}
            </div>
          ) : (
            '—'
          ),
      },
      {
        title: (
          <Tooltip title="近6年历史最高价（A股前复权）">
            <span>最高价</span>
          </Tooltip>
        ),
        dataIndex: 'histHigh',
        render: (value, record) =>
          value != null ? formatMarketPrice(value, record.code) : '—',
      },
      {
        title: (
          <Tooltip title="现价相对近6年最高价的涨跌幅">
            <span>降幅</span>
          </Tooltip>
        ),
        key: 'histHighDrop',
        render: (_, record) => renderHistHighDropPct(record.histHigh, record.priceNow),
      },
      {
        title: 'PB',
        dataIndex: 'pb',
        render: (value) => formatRatio(value),
      },
      {
        title: 'PE(TTM)',
        dataIndex: 'pe',
        render: (value) => formatRatio(value),
      },
      {
        title: (
          <Tooltip title="按 PB / PE(TTM) 估算：ROE ≈ PB / PE">
            <span>ROE</span>
          </Tooltip>
        ),
        key: 'roe',
        render: (_, record) => formatPercent(calcRoeFromPbPe(record.pb, record.pe)),
      },
      {
        title: '左侧点',
        dataIndex: 'leftPoint',
        render: (value, record) => renderBuyPoint(value, record),
      },
      {
        title: '趋势点',
        dataIndex: 'trendPoint',
        render: (value, record) => renderTrendPoint(value, record),
      },
      {
        title: '血筹点',
        dataIndex: 'bloodPoint',
        render: (value, record) => renderBuyPoint(value, record),
      },
    ],
    [isMobile, profitColor, lossColor, colorFromValue, highlightStyle, token.colorTextDisabled],
  );

  return (
    <Table
      rowKey="code"
      columns={columns}
      dataSource={data}
      loading={loading}
      pagination={false}
      onRow={(record) => ({
        onClick: () => handleRowClick(record),
        style: { cursor: 'pointer' },
      })}
      scroll={isMobile ? { x: 'max-content' } : undefined}
      size={isMobile ? 'small' : 'middle'}
      tableLayout="auto"
    />
  );
};
