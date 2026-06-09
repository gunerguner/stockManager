import { Descriptions, Table, Tooltip } from 'antd';
import { useMemo } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useCommonModal } from '@/components/Common/useCommonModal';
import { useIsMobile } from '@/hooks/useIsMobile';
import { formatMarketPrice, isHkCode, toXueqiuStockUrl } from '@/utils/format/stock';
import { renderHoldingStatus } from '@/utils/format/render';

type WatchTableProps = {
  data: API.WatchItem[];
  loading?: boolean;
};

const isBuyPointTriggered = (priceNow: number | null, point: number | null): boolean =>
  priceNow != null && point != null && point > 0 && priceNow <= point * 1.05;

const isTrendPointTriggered = (priceNow: number | null, point: number | null): boolean =>
  priceNow != null && point != null && point > 0 && priceNow > point;

const rowTriggered = (record: API.WatchItem): boolean =>
  isBuyPointTriggered(record.priceNow, record.leftPoint) ||
  isBuyPointTriggered(record.priceNow, record.bloodPoint) ||
  isTrendPointTriggered(record.priceNow, record.trendPoint);

const formatRatio = (value: number | null): string =>
  value != null && !Number.isNaN(value) ? value.toFixed(2) : '—';

const renderMultilineText = (text: string) => {
  if (!text) return '—';
  return <span style={{ whiteSpace: 'pre-wrap' }}>{text}</span>;
};

const highlightedPointStyle: React.CSSProperties = {
  color: '#cf1322',
  fontWeight: 600,
  background: '#fff1f0',
  padding: '2px 6px',
  borderRadius: 4,
};

const renderBuyPoint = (val: number | null, record: API.WatchItem) => {
  if (val == null || val <= 0) return <span style={{ color: '#bbb' }}>—</span>;
  const hit = isBuyPointTriggered(record.priceNow, val);
  return (
    <span style={hit ? highlightedPointStyle : undefined}>
      {formatMarketPrice(val, record.code)}
    </span>
  );
};

const renderTrendPoint = (val: number | null, record: API.WatchItem) => {
  if (val == null || val <= 0) return <span style={{ color: '#bbb' }}>—</span>;
  const hit = isTrendPointTriggered(record.priceNow, val);
  return (
    <span style={hit ? highlightedPointStyle : undefined}>
      {formatMarketPrice(val, record.code)}
    </span>
  );
};

export const WatchTable: React.FC<WatchTableProps> = ({ data, loading = false }) => {
  const isMobile = useIsMobile();
  const { showModal } = useCommonModal();

  const handleRowClick = (record: API.WatchItem) => {
    showModal({
      title: `${record.name}（${record.code}）`,
      width: 768,
      content: (
        <Descriptions bordered column={1} size="small">
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
          }),
      },
      {
        title: '现价',
        dataIndex: 'priceNow',
        render: (value, record) =>
          value != null ? formatMarketPrice(value, record.code) : '—',
      },
      {
        title: (
          <Tooltip title="近6年历史最高价（A股前复权）">
            <span>6年内高</span>
          </Tooltip>
        ),
        dataIndex: 'histHigh',
        render: (value, record) =>
          value != null ? formatMarketPrice(value, record.code) : '—',
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
    [isMobile],
  );

  return (
    <Table
      rowKey="code"
      columns={columns}
      dataSource={data}
      loading={loading}
      bordered
      pagination={false}
      onRow={(record) => ({
        onClick: () => handleRowClick(record),
        style: {
          cursor: 'pointer',
          background: rowTriggered(record) ? '#fff7e6' : undefined,
        },
      })}
      scroll={isMobile ? { x: 'max-content' } : undefined}
      size={isMobile ? 'small' : 'middle'}
      tableLayout="auto"
    />
  );
};
