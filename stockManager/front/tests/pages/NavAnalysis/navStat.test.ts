import {
  downsampleNavPoints,
  excessReturnVs,
  rebaseNavPoints,
} from '@/pages/NavAnalysis/components/navStat';

const closes = (
  hs300: number | null,
  cyb: number | null = null,
  kc50: number | null = null,
): API.NavBenchmarkCloses => ({ hs300, cyb, kc50 });

const point = (
  date: string,
  nav = 1,
  benchmarks?: API.NavBenchmarkCloses,
): API.NavPoint => ({ date, nav, navDisplay: nav, benchmarks });

const metas: API.NavBenchmarkMeta[] = [
  { key: 'hs300', code: 'sh000300', name: '沪深300', availableFrom: '2005-04-08' },
  { key: 'cyb', code: 'sz399006', name: '创业板指', availableFrom: '2010-06-01' },
  { key: 'kc50', code: 'sh000688', name: '科创50', availableFrom: '2020-07-23' },
];

test('downsampleNavPoints keeps first last and keepDates', () => {
  const points = [
    point('2024-01-01'),
    point('2024-01-02'),
    point('2024-01-03'),
    point('2024-01-04'),
    point('2024-01-05'),
    point('2024-01-06'),
  ];
  const sampled = downsampleNavPoints(points, 2, ['2024-01-03']);
  expect(sampled[0].date).toBe('2024-01-01');
  expect(sampled.at(-1)?.date).toBe('2024-01-06');
  expect(sampled.map((p) => p.date)).toContain('2024-01-03');
});

test('downsampleNavPoints returns original when too short', () => {
  const points = [point('2024-01-01'), point('2024-01-02')];
  expect(downsampleNavPoints(points, 5)).toEqual(points);
});

test('rebase uses sampled first point as the shared anchor', () => {
  const points = [
    point('2024-01-01', 2, closes(100, 50, null)),
    point('2024-01-02', 2.2, closes(110, 55, null)),
    point('2024-01-03', 2.4, closes(null, 60, 80)),
    point('2024-01-04', 2.6, closes(130, 65, 88)),
    point('2024-01-05', 2.8, closes(140, 70, 90)),
    point('2024-01-06', 3, closes(150, 75, 100)),
  ];
  const sampled = downsampleNavPoints(points, 5);
  const series = rebaseNavPoints(sampled, metas);
  expect(sampled[0].date).toBe('2024-01-01');
  expect(series.portfolio[0]).toBe(1);
  expect(series.portfolio.at(-1)).toBeCloseTo(1.5);
  const hs300 = series.lines.find((line) => line.key === 'hs300');
  expect(hs300?.sharedAnchor).toBe(true);
  expect(hs300?.values[0]).toBe(1);
  expect(hs300?.values.at(-1)).toBeCloseTo(1.5);
});

test('rebase leaves a missing session empty', () => {
  const points = [
    point('2024-01-02', 1, closes(100)),
    point('2024-01-03', 1.1, closes(null)),
    point('2024-01-04', 1.2, closes(110)),
  ];
  const hs300 = rebaseNavPoints(points, metas).lines.find((line) => line.key === 'hs300');
  expect(hs300?.values).toEqual([1, null, 1.1]);
});

test('excessReturnVs uses the same window anchor as the index', () => {
  const points = [
    point('2024-01-02', 1, closes(100)),
    point('2024-06-03', 1.2, closes(110)),
  ];
  expect(excessReturnVs(points, 'all', 'hs300')).toBeCloseTo(1.2 / 1.1 - 1);
  expect(excessReturnVs([point('2024-01-02', 1, closes(null))], 'all', 'hs300')).toBeNull();
  expect(
    excessReturnVs(
      [point('2024-01-02', 1, closes(null)), point('2024-01-03', 1.1, closes(100))],
      'all',
      'hs300',
    ),
  ).toBeNull();
});

test('rebase starts a late index at its own first close', () => {
  const points = [
    point('2019-01-02', 1, closes(3000, 1800, null)),
    point('2020-07-23', 1.2, closes(3300, 2000, 1000)),
    point('2020-07-24', 1.3, closes(3400, 2100, 1100)),
  ];
  const kc50 = rebaseNavPoints(points, metas).lines.find((line) => line.key === 'kc50');
  expect(kc50?.sharedAnchor).toBe(false);
  expect(kc50?.startDate).toBe('2020-07-23');
  expect(kc50?.values).toEqual([null, 1, 1.1]);
});
