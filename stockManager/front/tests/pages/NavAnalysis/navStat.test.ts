import { downsampleNavPoints } from '@/pages/NavAnalysis/components/navStat';

const point = (date: string, nav = 1): API.NavPoint => ({ date, nav, navDisplay: nav });

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
