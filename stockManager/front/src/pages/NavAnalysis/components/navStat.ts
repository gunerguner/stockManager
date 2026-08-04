import dayjs from 'dayjs';

export type NavRangeKey = 'all' | 'ytd' | 'oneYear';

/** 「全部」区间图表采样步长（交易日点数，非整日历天） */
const ALL_RANGE_CHART_STEP = 5;

export const NAV_RANGE_OPTIONS: { key: NavRangeKey; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'ytd', label: '本年度' },
  { key: 'oneYear', label: '近一年' },
];

function insertKeepDates(
  points: API.NavPoint[],
  sampled: API.NavPoint[],
  keepDates: string[],
): API.NavPoint[] {
  if (!keepDates.length) return sampled;
  const byDate = new Map(points.map((p) => [p.date, p]));
  const result = [...sampled];
  const present = new Set(result.map((p) => p.date));
  for (const date of keepDates) {
    if (present.has(date)) continue;
    const point = byDate.get(date);
    if (!point) continue;
    const insertAt = result.findIndex((p) => p.date > date);
    if (insertAt === -1) {
      result.push(point);
    } else {
      result.splice(insertAt, 0, point);
    }
    present.add(date);
  }
  return result;
}

/** 按步长降采样；始终保留首尾，并插入 keepDates（最高/回撤锚点）。 */
export function downsampleNavPoints(
  points: API.NavPoint[],
  step: number,
  keepDates: string[] = [],
): API.NavPoint[] {
  if (points.length <= 2 || step <= 1) {
    return insertKeepDates(points, [...points], keepDates);
  }
  const sampled: API.NavPoint[] = [];
  for (let i = 0; i < points.length; i += step) {
    sampled.push(points[i]);
  }
  const last = points[points.length - 1];
  if (sampled[sampled.length - 1]?.date !== last.date) {
    sampled.push(last);
  }
  return insertKeepDates(points, sampled, keepDates);
}

/** 仅按区间切日期，不降采样 */
export function sliceNavPointsByRange(
  points: API.NavPoint[],
  range: NavRangeKey,
): API.NavPoint[] {
  if (!points.length || range === 'all') return points;
  const today = dayjs();
  const start =
    range === 'ytd' ? today.startOf('year') : today.subtract(1, 'year');
  return points.filter((p) => !dayjs(p.date).isBefore(start, 'day'));
}

/** 按快筛切片展示点（不重算摊入；指标直接取后端 metrics[range]） */
export function filterNavPoints(
  points: API.NavPoint[],
  range: NavRangeKey,
  keepDates: string[] = [],
): API.NavPoint[] {
  const sliced = sliceNavPointsByRange(points, range);
  if (!sliced.length) return sliced;
  if (range === 'all') {
    return downsampleNavPoints(sliced, ALL_RANGE_CHART_STEP, keepDates);
  }
  return sliced;
}

export function emptyNavMetrics(): API.NavMetrics {
  return {
    annualizedReturn: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    calmarRatio: 0,
    maxNav: null,
    drawdown: null,
  };
}

export function navKeepDates(metrics: API.NavMetrics): string[] {
  const { maxNav, drawdown } = metrics;
  return [
    maxNav?.date,
    drawdown?.peakDate,
    drawdown?.troughDate,
    drawdown?.endDate,
  ].filter((d): d is string => Boolean(d));
}
