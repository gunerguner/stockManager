import { useCallback, useMemo, useState } from 'react';
import { Empty, Spin, Typography } from 'antd';
import { useIsMobile } from '@/hooks/useIsMobile';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { NavChart } from './NavChart';
import { NavMetricsPanel } from './NavMetrics';
import {
  BENCHMARK_LINE_COLOR,
  emptyNavMetrics,
  excessReturnVs,
  filterNavPoints,
  navHasBenchmarkClose,
  navKeepDates,
  type NavRangeKey,
} from './navStat';
import './index.less';

const EMPTY_BENCHMARKS: API.NavBenchmarkMeta[] = [];

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
  const { colorFromValue } = useProfitLossColors();
  const [showDrawdown, setShowDrawdown] = useState(false);
  const [hiddenKeys, setHiddenKeys] = useState<API.NavBenchmarkKey[]>([]);
  const onHiddenKeysChange = useCallback((keys: API.NavBenchmarkKey[]) => {
    setHiddenKeys(keys);
  }, []);

  const metrics = data?.metrics?.[range] ?? emptyNavMetrics();
  const keepDates = useMemo(() => navKeepDates(metrics), [metrics]);

  const filteredPoints = useMemo(
    () => filterNavPoints(data?.points ?? [], range, keepDates),
    [data?.points, range, keepDates],
  );
  const latestNav = data?.points?.at(-1)?.navDisplay ?? null;
  const benchmarks = data?.benchmarks ?? EMPTY_BENCHMARKS;
  const excessByKey = useMemo(() => {
    const points = data?.points ?? [];
    return {
      hs300: excessReturnVs(points, range, 'hs300'),
      cyb: excessReturnVs(points, range, 'cyb'),
      kc50: excessReturnVs(points, range, 'kc50'),
    };
  }, [data?.points, range]);
  const benchmarkSynced = navHasBenchmarkClose(data?.points ?? []);

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
            {benchmarks.length > 0 ? (
              <div className="nav-excess" aria-label="区间超额">
                <span className="nav-excess__label">区间超额</span>
                {benchmarks.map((meta) => {
                  const excess = excessByKey[meta.key];
                  const text =
                    excess == null
                      ? '—'
                      : `${excess > 0 ? '+' : ''}${(excess * 100).toFixed(2)}%`;
                  return (
                    <span className="nav-excess__item" key={meta.key}>
                      <i
                        className="nav-excess__swatch"
                        style={{ background: BENCHMARK_LINE_COLOR[meta.key] }}
                      />
                      <span>{meta.name}</span>
                      <strong style={{ color: excess == null ? undefined : colorFromValue(excess) }}>
                        {text}
                      </strong>
                    </span>
                  );
                })}
              </div>
            ) : null}
            <NavChart
              points={filteredPoints}
              benchmarks={benchmarks}
              hiddenKeys={hiddenKeys}
              onHiddenKeysChange={onHiddenKeysChange}
              height={isMobile ? 280 : 380}
              maxNav={metrics.maxNav}
              drawdown={metrics.drawdown}
              showDrawdown={showDrawdown}
            />
            {benchmarks.length > 0 ? (
              <Typography.Text type="secondary" className="nav-chart__note">
                指数为价格指数，不含分红；组合净值含分红。虚线表示该指数在区间起点尚无行情，从自身起点归一，不计算超额。
                {benchmarkSynced ? '' : ' 指数尚未同步，请点「增量刷新」。'}
              </Typography.Text>
            ) : null}
          </div>
        </>
      )}
    </Spin>
  );
};
