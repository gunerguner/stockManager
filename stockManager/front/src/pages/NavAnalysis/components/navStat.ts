import dayjs from 'dayjs';

export type NavRangeKey = 'all' | 'ytd' | 'oneYear';

/** 「全部」区间图表采样步长（交易日点数，非整日历天） */
const ALL_RANGE_CHART_STEP = 5;

export const NAV_RANGE_OPTIONS: { key: NavRangeKey; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'ytd', label: '本年度' },
  { key: 'oneYear', label: '近一年' },
];

/** 按步长降采样；始终保留首尾点，避免曲线端点漂移。 */
export function downsampleNavPoints(
  points: API.NavPoint[],
  step: number,
): API.NavPoint[] {
  if (points.length <= 2 || step <= 1) return points;
  const sampled: API.NavPoint[] = [];
  for (let i = 0; i < points.length; i += step) {
    sampled.push(points[i]);
  }
  const last = points[points.length - 1];
  if (sampled[sampled.length - 1]?.date !== last.date) {
    sampled.push(last);
  }
  return sampled;
}

/** 按快筛切片展示点（不重算摊入；指标直接取后端 metrics[range]） */
export function filterNavPoints(
  points: API.NavPoint[],
  range: NavRangeKey,
): API.NavPoint[] {
  if (!points.length) return points;
  if (range === 'all') {
    return downsampleNavPoints(points, ALL_RANGE_CHART_STEP);
  }
  const today = dayjs();
  const start =
    range === 'ytd' ? today.startOf('year') : today.subtract(1, 'year');
  return points.filter((p) => !dayjs(p.date).isBefore(start, 'day'));
}

export function emptyNavMetrics(): API.NavMetrics {
  return {
    annualizedReturn: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    calmarRatio: 0,
  };
}
