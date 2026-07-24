import { Button, Descriptions, Table, Tooltip, theme } from 'antd';
import { useMemo, useState } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useCommonModal } from '@/components/Common/modal/useCommonModal';
import { getResponsiveTableProps, useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { formatPercent } from '@/utils/format/stock';
import { HoldingStatus } from '@/components/Common/HoldingStatus';
import { renderDailyChange } from '@/utils/format/render';
import {
  calcHistHighDropPct,
  calcRoeFromPbPe,
  formatDecimal,
  formatMarketPriceOrDash,
  isBuyPointTriggered,
  isBuyPointWarning,
  isTrendPointTriggered,
  isTrendPointWarning,
} from './watchHelpers';
import '@/components/Common/index.less';

type WatchTableProps = {
  data: API.WatchItem[];
  loading?: boolean;
  onToggleHidden?: (record: API.WatchItem, nextHidden: boolean) => Promise<boolean>;
};

const renderMultilineText = (text: string) => {
  if (!text) return '—';
  return <span style={{ whiteSpace: 'pre-wrap' }}>{text}</span>;
};

const WatchDetailContent: React.FC<{
  record: API.WatchItem;
  onToggleHidden?: (record: API.WatchItem, nextHidden: boolean) => Promise<boolean>;
  onClose: () => void;
}> = ({ record, onToggleHidden, onClose }) => {
  const [submitting, setSubmitting] = useState(false);

  const handleToggle = async () => {
    if (!onToggleHidden) return;
    setSubmitting(true);
    try {
      const ok = await onToggleHidden(record, !record.hidden);
      if (ok) onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Descriptions column={1} size="small" className="watch-detail-descriptions">
        <Descriptions.Item label="风险">{renderMultilineText(record.risk)}</Descriptions.Item>
        <Descriptions.Item label="机会">{renderMultilineText(record.opportunity)}</Descriptions.Item>
        <Descriptions.Item label="左侧点">
          {formatMarketPriceOrDash(record.leftPoint, record.code)}
        </Descriptions.Item>
        <Descriptions.Item label="趋势点">
          {formatMarketPriceOrDash(record.trendPoint, record.code)}
        </Descriptions.Item>
        <Descriptions.Item label="血筹点">
          {formatMarketPriceOrDash(record.bloodPoint, record.code)}
        </Descriptions.Item>
        <Descriptions.Item label="现价">
          {formatMarketPriceOrDash(record.priceNow, record.code)}
        </Descriptions.Item>
        <Descriptions.Item label="6年内最高">
          {formatMarketPriceOrDash(record.histHigh, record.code)}
        </Descriptions.Item>
        <Descriptions.Item label="PB">{formatDecimal(record.pb)}</Descriptions.Item>
        <Descriptions.Item label="PE(TTM)">{formatDecimal(record.pe)}</Descriptions.Item>
        <Descriptions.Item label="ROE">
          {formatPercent(calcRoeFromPbPe(record.pb, record.pe))}
        </Descriptions.Item>
      </Descriptions>
      {onToggleHidden && (
        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <Button type="primary" ghost loading={submitting} onClick={handleToggle}>
            {record.hidden ? '显示' : '隐藏'}
          </Button>
        </div>
      )}
    </>
  );
};

export const WatchTable: React.FC<WatchTableProps> = ({
  data,
  loading = false,
  onToggleHidden,
}) => {
  const isMobile = useIsMobile();
  const { showModal } = useCommonModal();
  const { colorFromValue, highlightStyle, warningStyle } = useProfitLossColors();
  const { token } = theme.useToken();

  const renderHistHighDropPct = (histHigh: number | null, priceNow: number | null): React.ReactNode => {
    const dropPct = calcHistHighDropPct(histHigh, priceNow);
    if (dropPct == null) return '—';
    return (
      <span style={{ color: colorFromValue(dropPct) }}>{formatPercent(dropPct)}</span>
    );
  };

  const renderBuyPoint = (val: number | null, record: API.WatchItem) => {
    if (val == null || val <= 0) {
      return <span style={{ color: token.colorTextDisabled }}>—</span>;
    }
    const hit = isBuyPointTriggered(record.priceNow, val);
    const warning = isBuyPointWarning(record.priceNow, val);
    return (
      <span style={hit ? highlightStyle : warning ? warningStyle : undefined}>
        {formatMarketPriceOrDash(val, record.code)}
      </span>
    );
  };

  const renderTrendPoint = (val: number | null, record: API.WatchItem) => {
    if (val == null || val <= 0) {
      return <span style={{ color: token.colorTextDisabled }}>—</span>;
    }
    const hit = isTrendPointTriggered(record.priceNow, val);
    const warning = isTrendPointWarning(record.priceNow, val);
    return (
      <span style={hit ? highlightStyle : warning ? warningStyle : undefined}>
        {formatMarketPriceOrDash(val, record.code)}
      </span>
    );
  };

  const handleRowClick = (record: API.WatchItem) => {
    const closeRef = { current: () => {} };
    const { destroy } = showModal({
      title: `${record.name}（${record.code}）`,
      width: isMobile ? undefined : 768,
      content: (
        <WatchDetailContent
          record={record}
          onToggleHidden={onToggleHidden}
          onClose={() => closeRef.current()}
        />
      ),
    });
    closeRef.current = destroy;
  };

  const columns: ColumnsType<API.WatchItem> = useMemo(
    () => [
      {
        title: '名称',
        dataIndex: 'name',
        width: isMobile ? 100 : 140,
        fixed: 'left',
        render: (_, record) => <HoldingStatus name={record.name} code={record.code} />,
      },
      {
        title: '现价',
        dataIndex: 'priceNow',
        width: isMobile ? 70 : 90,
        render: (value, record) => formatMarketPriceOrDash(value, record.code),
      },
      {
        title: '涨跌',
        dataIndex: 'offsetTodayRatio',
        width: isMobile ? 90 : 110,
        render: (_, record) =>
          renderDailyChange(record.offsetToday, record.offsetTodayRatio, record.code, colorFromValue, {
            priceNow: record.priceNow,
          }),
      },
      {
        title: (
          <Tooltip title="近6年历史最高价（A股前复权）">
            <span>最高价</span>
          </Tooltip>
        ),
        dataIndex: 'histHigh',
        width: isMobile ? 70 : 90,
        render: (value, record) => formatMarketPriceOrDash(value, record.code),
      },
      {
        title: (
          <Tooltip title="现价相对近6年最高价的涨跌幅">
            <span>降幅</span>
          </Tooltip>
        ),
        key: 'histHighDrop',
        width: isMobile ? 60 : 80,
        render: (_, record) => renderHistHighDropPct(record.histHigh, record.priceNow),
      },
      {
        title: 'PB',
        dataIndex: 'pb',
        width: isMobile ? 55 : 70,
        render: (value) => formatDecimal(value),
      },
      {
        title: 'PE(TTM)',
        dataIndex: 'pe',
        width: isMobile ? 60 : 80,
        render: (value) => formatDecimal(value),
      },
      {
        title: (
          <Tooltip title="按 PB / PE(TTM) 估算：ROE ≈ PB / PE">
            <span>ROE</span>
          </Tooltip>
        ),
        key: 'roe',
        width: isMobile ? 60 : 80,
        render: (_, record) => formatPercent(calcRoeFromPbPe(record.pb, record.pe)),
      },
      {
        title: '左侧点',
        dataIndex: 'leftPoint',
        width: isMobile ? 65 : 80,
        render: (value, record) => renderBuyPoint(value, record),
      },
      {
        title: '趋势点',
        dataIndex: 'trendPoint',
        width: isMobile ? 65 : 80,
        render: (value, record) => renderTrendPoint(value, record),
      },
      {
        title: '血筹点',
        dataIndex: 'bloodPoint',
        width: isMobile ? 65 : 80,
        render: (value, record) => renderBuyPoint(value, record),
      },
    ],
    [isMobile, colorFromValue, highlightStyle, warningStyle, token.colorTextDisabled],
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
      {...getResponsiveTableProps(isMobile)}
    />
  );
};
