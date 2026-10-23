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
  const present = new Set(sampled.map((p) => p.date));
  const extras = keepDates.flatMap((date) => {
    const point = byDate.get(date);
    if (!point || present.has(date)) return [];
    present.add(date);
    return [point];
  });
  return extras.length
    ? [...sampled, ...extras].toSorted((a, b) => a.date.localeCompare(b.date))
    : sampled;
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
  const sampled = points.filter((_, i) => i % step === 0);
  const last = points.at(-1)!;
  if (sampled.at(-1)?.date !== last.date) {
    sampled.push(last);
  }
  return insertKeepDates(points, sampled, keepDates);
}

/** 仅按区间切日期，不降采样。以上一周期最后交易日收盘为起点，计入窗口首日涨跌。 */
export function sliceNavPointsByRange(
  points: API.NavPoint[],
  range: NavRangeKey,
): API.NavPoint[] {
  if (!points.length || range === 'all') return points;
  const today = dayjs();
  const windowStart =
    range === 'ytd' ? today.startOf('year') : today.subtract(1, 'year');
  const split = points.findIndex(
    (p) => !dayjs(p.date).isBefore(windowStart, 'day'),
  );
  if (split === -1) return points.slice(-1);
  if (split === 0) return points;
  return points.slice(split - 1);
}

/** 相对某指数的累计超额：(组合区间涨跌+1) / (指数区间涨跌+1) - 1。锚点当天没有指数收盘时返回 null。 */
export function excessReturnVs(
  points: API.NavPoint[],
  range: NavRangeKey,
  key: API.NavBenchmarkKey,
): number | null {
  const sliced = sliceNavPointsByRange(points, range);
  if (sliced.length < 2) return null;
  const start = sliced[0];
  const end = sliced.at(-1)!;
  const navStart = start.navDisplay;
  const navEnd = end.navDisplay;
  const idxStart = start.benchmarks?.[key];
  const idxEnd = end.benchmarks?.[key];
  if (
    !positiveClose(navStart) ||
    !positiveClose(navEnd) ||
    !positiveClose(idxStart) ||
    !positiveClose(idxEnd)
  ) {
    return null;
  }
  return navEnd / navStart / (idxEnd / idxStart) - 1;
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
    totalReturn: 0,
    annualizedReturn: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    calmarRatio: 0,
    maxNav: null,
    drawdown: null,
  };
}

const BENCHMARK_KEYS = ['hs300', 'cyb', 'kc50'] as const;

export const BENCHMARK_LINE_COLOR: Record<API.NavBenchmarkKey, string> = {
  hs300: '#8B5CF6',
  cyb: '#F6BD16',
  kc50: '#5AD8A6',
};

function isBenchmarkKey(key: string): key is API.NavBenchmarkKey {
  return (BENCHMARK_KEYS as readonly string[]).includes(key);
}

export function excessByBenchmark(
  points: API.NavPoint[],
  range: NavRangeKey,
): Record<API.NavBenchmarkKey, number | null> {
  return Object.fromEntries(
    BENCHMARK_KEYS.map((key) => [key, excessReturnVs(points, range, key)]),
  ) as Record<API.NavBenchmarkKey, number | null>;
}

function positiveClose(value: number | null | undefined): value is number {
  return value != null && value > 0;
}

export type RebasedBenchmarkLine = {
  key: API.NavBenchmarkKey;
  name: string;
  sharedAnchor: boolean;
  startDate: string | null;
  values: (number | null)[];
};

/** 组合与指数都相对当前序列第一个点归一。指数在锚点无收盘时改用自身首个有效点。 */
export function rebaseNavPoints(
  points: API.NavPoint[],
  metas: API.NavBenchmarkMeta[],
): { portfolio: number[]; lines: RebasedBenchmarkLine[] } {
  const displays = points.map((point) => point.navDisplay);
  const base = displays[0];
  const portfolio =
    base != null && base > 0 ? displays.map((value) => value / base) : displays;

  const lines = metas.flatMap((meta): RebasedBenchmarkLine[] => {
    if (!isBenchmarkKey(meta.key)) return [];
    const closes = points.map((point) => point.benchmarks?.[meta.key] ?? null);
    const anchorClose = closes[0];
    if (positiveClose(anchorClose)) {
      return [
        {
          key: meta.key,
          name: meta.name,
          sharedAnchor: true,
          startDate: points[0]?.date ?? null,
          values: closes.map((close) =>
            positiveClose(close) ? close / anchorClose : null,
          ),
        },
      ];
    }
    const firstIdx = closes.findIndex((close) => positiveClose(close));
    if (firstIdx < 0) {
      return [
        {
          key: meta.key,
          name: meta.name,
          sharedAnchor: false,
          startDate: null,
          values: closes.map(() => null),
        },
      ];
    }
    const ownBase = closes[firstIdx] as number;
    return [
      {
        key: meta.key,
        name: meta.name,
        sharedAnchor: false,
        startDate: points[firstIdx]?.date ?? null,
        values: closes.map((close, index) =>
          index >= firstIdx && positiveClose(close) ? close / ownBase : null,
        ),
      },
    ];
  });

  return { portfolio, lines };
}

export function navHasBenchmarkClose(points: API.NavPoint[]): boolean {
  return points.some((point) =>
    BENCHMARK_KEYS.some((key) => point.benchmarks?.[key] != null),
  );
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
