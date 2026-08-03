import { useMemo } from 'react';
import { Empty, Spin } from 'antd';
import { useIsMobile } from '@/hooks/useIsMobile';
import { NavChart } from './NavChart';
import { NavMetricsPanel } from './NavMetrics';
import {
  emptyNavMetrics,
  filterNavPoints,
  type NavRangeKey,
} from './navStat';

type NavContentProps = {
  data: API.NavAnalysisData | null;
  range: NavRangeKey;
  loading?: boolean;
  refreshing?: boolean;
};

export const NavContent: React.FC<NavContentProps> = ({
  data,
  range,
  loading = false,
  refreshing = false,
}) => {
  const isMobile = useIsMobile();

  const filteredPoints = useMemo(
    () => filterNavPoints(data?.points ?? [], range),
    [data?.points, range],
  );
  const metrics = data?.metrics?.[range] ?? emptyNavMetrics();
  const latestNav = data?.points?.length
    ? data.points[data.points.length - 1].navDisplay
    : null;

  return (
    <Spin spinning={loading || refreshing}>
      {!loading && filteredPoints.length === 0 ? (
        <Empty
          description="暂无净值数据，请先点击「全量刷新」生成"
          style={{ padding: '48px 0' }}
        />
      ) : (
        <>
          <NavMetricsPanel metrics={metrics} latestNav={latestNav} />
          <div style={{ marginTop: 16 }}>
            <NavChart
              points={filteredPoints}
              height={isMobile ? 280 : 380}
            />
          </div>
        </>
      )}
    </Spin>
  );
};
