import React from 'react';
import { Col, Row, Statistic, Typography, theme } from 'antd';
import { getHeaderStatisticStyles } from '@/components/Common/statisticStyles';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';

type NavMetricsProps = {
  metrics: API.NavMetrics;
  latestNav?: number | null;
  showDrawdown?: boolean;
  onToggleDrawdown?: () => void;
};

export const NavMetricsPanel: React.FC<NavMetricsProps> = ({
  metrics,
  latestNav,
  showDrawdown = false,
  onToggleDrawdown,
}) => {
  const isMobile = useIsMobile();
  const { colorFromValue } = useProfitLossColors();
  const { token } = theme.useToken();

  const canToggleDrawdown =
    Boolean(onToggleDrawdown) &&
    Boolean(metrics.drawdown) &&
    Math.abs(metrics.maxDrawdown) > 1e-12;

  const items: {
    title: string;
    value: number;
    precision: number;
    suffix?: string;
    color?: string;
    clickable?: boolean;
  }[] = [
    ...(latestNav != null
      ? [
          {
            title: '最新净值',
            value: latestNav,
            precision: 4,
            color: colorFromValue(latestNav - 1),
          },
        ]
      : []),
    {
      title: '年化收益',
      value: metrics.annualizedReturn * 100,
      precision: 2,
      suffix: '%',
      color: colorFromValue(metrics.annualizedReturn),
    },
    {
      title: '夏普比率',
      value: metrics.sharpeRatio,
      precision: 2,
      color: colorFromValue(metrics.sharpeRatio),
    },
    {
      title: '最大回撤',
      value: metrics.maxDrawdown * 100,
      precision: 2,
      suffix: '%',
      color: colorFromValue(metrics.maxDrawdown),
      clickable: canToggleDrawdown,
    },
    {
      title: '卡玛比率',
      value: metrics.calmarRatio,
      precision: 2,
      color: colorFromValue(metrics.calmarRatio),
    },
  ];

  return (
    <>
      <Row gutter={[16, 12]}>
        {items.map((item) => {
          const isDrawdown = item.title === '最大回撤';
          const active = isDrawdown && showDrawdown;
          return (
            <Col key={item.title} xs={12} sm={8} md={4}>
              <div
                role={item.clickable ? 'button' : undefined}
                tabIndex={item.clickable ? 0 : undefined}
                title={
                  item.clickable
                    ? showDrawdown
                      ? '点击关闭图表上回撤标注'
                      : '点击在图表上标注回撤区间'
                    : undefined
                }
                aria-pressed={item.clickable ? showDrawdown : undefined}
                onClick={item.clickable ? onToggleDrawdown : undefined}
                onKeyDown={
                  item.clickable
                    ? (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          onToggleDrawdown?.();
                        }
                      }
                    : undefined
                }
                style={{
                  cursor: item.clickable ? 'pointer' : undefined,
                  borderRadius: token.borderRadius,
                  padding: active ? '4px 8px' : undefined,
                  margin: active ? '-4px -8px' : undefined,
                  background: active ? token.colorErrorBg : undefined,
                  outline: active
                    ? `1px solid ${token.colorErrorBorder}`
                    : undefined,
                }}
              >
                <Statistic
                  title={item.title}
                  value={item.value}
                  precision={item.precision}
                  suffix={item.suffix}
                  styles={getHeaderStatisticStyles(isMobile, item.color)}
                />
              </div>
            </Col>
          );
        })}
      </Row>
      <Typography.Paragraph
        type="secondary"
        style={{ marginTop: 12, marginBottom: 0, fontSize: 12 }}
      >
        净值年化为时间加权（剔出入金），与资金加权的 XIRR 口径不同。夏普无风险利率按 0
        计算。点击「最大回撤」可在图表标注回撤起止与收复。
      </Typography.Paragraph>
    </>
  );
};
