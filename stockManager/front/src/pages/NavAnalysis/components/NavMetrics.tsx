import React from 'react';
import { Col, Row, Statistic, Typography } from 'antd';
import { getHeaderStatisticStyles } from '@/components/Common/statisticStyles';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';

type NavMetricsProps = {
  metrics: API.NavMetrics;
};

export const NavMetricsPanel: React.FC<NavMetricsProps> = ({ metrics }) => {
  const isMobile = useIsMobile();
  const { colorFromValue } = useProfitLossColors();

  const items: {
    title: string;
    value: number;
    precision: number;
    suffix?: string;
    color?: string;
  }[] = [
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
        {items.map((item) => (
          <Col key={item.title} xs={12} sm={6}>
            <Statistic
              title={item.title}
              value={item.value}
              precision={item.precision}
              suffix={item.suffix}
              styles={getHeaderStatisticStyles(isMobile, item.color)}
            />
          </Col>
        ))}
      </Row>
      <Typography.Paragraph
        type="secondary"
        style={{ marginTop: 12, marginBottom: 0, fontSize: 12 }}
      >
        净值年化为时间加权（剔出入金），与资金加权的 XIRR 口径不同。夏普无风险利率按 0
        计算。
      </Typography.Paragraph>
    </>
  );
};
