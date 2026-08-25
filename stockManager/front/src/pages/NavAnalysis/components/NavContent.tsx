import { useMemo, useState } from 'react';
import { Empty, Spin } from 'antd';
import { useIsMobile } from '@/hooks/useIsMobile';
import { NavChart } from './NavChart';
import { NavMetricsPanel } from './NavMetrics';
import {
  emptyNavMetrics,
  filterNavPoints,
  navKeepDates,
  type NavRangeKey,
} from './navStat';
import './index.less';

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
  const [showDrawdown, setShowDrawdown] = useState(false);

  const metrics = data?.metrics?.[range] ?? emptyNavMetrics();
  const keepDates = useMemo(() => navKeepDates(metrics), [metrics]);

  const filteredPoints = useMemo(
    () => filterNavPoints(data?.points ?? [], range, keepDates),
    [data?.points, range, keepDates],
  );
  const latestNav = data?.points?.at(-1)?.navDisplay ?? null;

  return (
    <Spin spinning={loading || refreshing}>
      {!loading && filteredPoints.length === 0 ? (
        <Empty
          description="暂无净值数据，请先点击「全量刷新」生成"
          styles={{ root: { padding: '48px 0' } }}
        />
      ) : (
        <>
          <NavMetricsPanel
            metrics={metrics}
            latestNav={latestNav}
            showDrawdown={showDrawdown}
            onToggleDrawdown={() => setShowDrawdown((v) => !v)}
          />
          <div className="nav-chart">
            <NavChart
              points={filteredPoints}
              height={isMobile ? 280 : 380}
              maxNav={metrics.maxNav}
              drawdown={metrics.drawdown}
              showDrawdown={showDrawdown}
            />
          </div>
        </>
      )}
    </Spin>
  );
};
