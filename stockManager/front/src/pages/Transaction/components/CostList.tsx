import { Col, Row, Spin, Statistic, theme, Typography } from 'antd';
import React, { useEffect, useMemo, useState } from 'react';
import { useIsMobile } from '@/hooks/useIsMobile';
import { getHeaderStatisticStyles } from '@/components/Common/statisticStyles';
import { useTradeDetailModal } from '@/components/Common/modal/TradeDetailModal';
import { buildCostListByPeriod, parseYearMonth, type CostListModel } from './costStat';
import { formatAmount } from '@/utils/format/stock';
import '@/components/Common/index.less';
import './index.less';

const { Link } = Typography;

export type CostListProps = {
  data: API.StockData;
  operations: Record<string, API.Operation[]>;
  loading?: boolean;
};

type CountType = 'normalTradeCount' | 'convTradeCount' | 'dividendCount';

/** 交易次数指标：key / 标题 / 过滤条件 */
const COUNT_METRICS: Array<{
  key: CountType;
  label: string;
  filter: (stock: API.Stock, op: API.Operation) => boolean;
}> = [
  { key: 'normalTradeCount', label: '普通交易', filter: (s, op) => s.stockType !== 'CONV' && op.type !== 'DV' },
  { key: 'convTradeCount', label: '可转债交易', filter: (s, op) => s.stockType === 'CONV' && op.type !== 'DV' },
  { key: 'dividendCount', label: '除权除息', filter: (_, op) => op.type === 'DV' },
];

/** 单个指标单元 */
const MetricCard: React.FC<{
  label: string;
  value: React.ReactNode;
  clickable?: boolean;
  onClick?: () => void;
}> = ({ label, value, clickable, onClick }) => {
  const { token } = theme.useToken();
  const valueColor = !clickable
    ? token.colorText
    : token.colorPrimary;
  return (
    <div
      className={`metric-card ${clickable ? 'metric-card--clickable' : 'metric-card--zero'}`}
      style={{ background: token.colorFillQuaternary }}
      onClick={onClick}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
    >
      <div className="metric-card__value" style={{ color: valueColor }}>
        {value}
      </div>
      <div className="metric-card__label" style={{ color: token.colorText }}>
        {label}
      </div>
    </div>
  );
};

/** 出入金渲染（正绿负红） */
const CashFlowValue: React.FC<{ value: number }> = ({ value }) => {
  const { token } = theme.useToken();
  const color = value > 0 ? token.colorSuccess : value < 0 ? token.colorError : undefined;
  const sign = value > 0 ? '+' : '';
  return (
    <span style={{ color }}>
      {sign}
      {formatAmount(value, { grouped: true })}
    </span>
  );
};

/** 资金动向金额指标：标题 / 渲染函数 */
const MONEY_METRICS: Array<{ label: string; render: (r: CostListModel) => React.ReactNode }> = [
  { label: '买入', render: (r) => formatAmount(r.buyAmount, { grouped: true }) },
  { label: '卖出', render: (r) => formatAmount(r.sellAmount, { grouped: true }) },
  { label: '出入金', render: (r) => <CashFlowValue value={r.cashFlow} /> },
  { label: '交易费', render: (r) => formatAmount(r.fee, { grouped: true }) },
];

/** 年度卡片紧凑指标行（7 个指标一行） */
const CompactMetricRow: React.FC<{
  record: CostListModel;
  onCountClick: (type: CountType) => void;
}> = ({ record, onCountClick }) => (
  <div className="metric-row">
    {COUNT_METRICS.map(({ key, label }) => {
      const value = record[key];
      const clickable = value > 0;
      return (
        <MetricCard
          key={key}
          label={label}
          value={value}
          clickable={clickable}
          onClick={clickable ? () => onCountClick(key) : undefined}
        />
      );
    })}
    {MONEY_METRICS.map(({ label, render }) => (
      <MetricCard key={label} label={label} value={render(record)} />
    ))}
  </div>
);

/** 月份迷你卡片 */
const MonthCard: React.FC<{
  record: CostListModel;
  parentYear: string;
  onCountClick: (type: CountType, year: string, month: string) => void;
}> = ({ record, parentYear, onCountClick }) => {
  const { token } = theme.useToken();
  return (
    <div className="month-card" style={{ background: token.colorFillQuaternary }}>
      <div className="month-card__title" style={{ color: token.colorText }}>
        {record.id} 月
      </div>
      <div
        className="month-card__section"
        style={{ borderTopColor: token.colorBorderSecondary }}
      >
        {COUNT_METRICS.map(({ key, label }) => {
          const value = record[key];
          const clickable = value > 0;
          return (
            <div
              key={key}
              className={`month-card__row ${clickable ? 'month-card__row--clickable' : ''}`}
              style={clickable ? { color: token.colorPrimary } : { color: token.colorText }}
              onClick={clickable ? () => onCountClick(key, parentYear, record.id) : undefined}
              role={clickable ? 'button' : undefined}
              tabIndex={clickable ? 0 : undefined}
            >
              <span>{label}</span>
              <span>{value}</span>
            </div>
          );
        })}
      </div>
      <div
        className="month-card__section"
        style={{ borderTopColor: token.colorBorderSecondary }}
      >
        {MONEY_METRICS.map(({ label, render }) => (
          <div key={label} className="month-card__row" style={{ color: token.colorText }}>
            <span>{label}</span>
            <span>{render(record)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/** 年度卡片 */
const YearCard: React.FC<{
  record: CostListModel;
  expanded: boolean;
  onToggle: () => void;
  onCountClick: (type: CountType, year: string, month?: string) => void;
}> = ({ record, expanded, onToggle, onCountClick }) => {
  const { token } = theme.useToken();
  return (
    <div
      className="year-card"
      style={{
        borderColor: token.colorBorderSecondary,
        background: token.colorBgContainer,
      }}
    >
      <div className="year-card__header">
        <span className="year-card__title" style={{ color: token.colorText }}>
          {record.id} 年度
        </span>
        <Link className="year-card__expand-btn" onClick={onToggle}>
          {expanded ? '收起' : '展开'}
        </Link>
      </div>
      <CompactMetricRow record={record} onCountClick={(type) => onCountClick(type, record.id)} />
      {expanded && (
        <div className="month-row" style={{ borderTopColor: token.colorBorderSecondary }}>
          {record.subList?.map((month) => (
            <MonthCard
              key={month.id}
              record={month}
              parentYear={record.id}
              onCountClick={onCountClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const CostList: React.FC<CostListProps> = ({
  data,
  operations,
  loading = false,
}) => {
  const { totalCost = 0 } = data.overall;
  const isMobile = useIsMobile();
  const { showTradeDetail } = useTradeDetailModal();

  const costList = useMemo(
    () => buildCostListByPeriod(data.stocks, operations, data.overall.cashFlowList),
    [data.stocks, operations, data.overall.cashFlowList],
  );

  const [expandedYears, setExpandedYears] = useState<Set<string>>(new Set());
  const hasInitRef = React.useRef(false);

  useEffect(() => {
    if (hasInitRef.current) return;
    if (costList.length === 0) return;
    hasInitRef.current = true;
    setExpandedYears(new Set([costList[0].id]));
  }, [costList]);

  const handleCountClick = (dataIndex: CountType, year: string, month?: string) => {
    const metric = COUNT_METRICS.find((m) => m.key === dataIndex);
    if (!metric) return;

    const filteredData = data.stocks
      .map((stock) => ({
        stock,
        operations: (operations[stock.code] || []).filter((op) => {
          const { year: opYear, month: opMonth } = parseYearMonth(op.date);
          return opYear === year && (!month || opMonth === month) && metric.filter(stock, op);
        }),
      }))
      .filter((item) => item.operations.length > 0);

    if (filteredData.length === 0) return;

    showTradeDetail({
      data: filteredData,
      title: `${year}年${month ? `${month}月` : ''}交易明细 - ${metric.label}`,
      displayType: 'tradeList',
    });
  };

  const toggleYear = (year: string) => {
    setExpandedYears((prev) => {
      const next = new Set(prev);
      if (next.has(year)) next.delete(year);
      else next.add(year);
      return next;
    });
  };

  return (
    <Spin spinning={loading}>
      <div className="cost-list-wrapper">
        <Row gutter={[16, 8]} className="table-list-header cost-list-header">
          <Col span={isMobile ? 24 : 6}>
            <Statistic
              title="总费用"
              value={totalCost}
              precision={2}
              styles={getHeaderStatisticStyles(isMobile)}
            />
          </Col>
        </Row>
        {costList.map((year) => (
          <YearCard
            key={year.id}
            record={year}
            expanded={expandedYears.has(year.id)}
            onToggle={() => toggleYear(year.id)}
            onCountClick={handleCountClick}
          />
        ))}
      </div>
    </Spin>
  );
};
