import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  TooltipComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { theme } from 'antd';
import { useModel } from '@umijs/max';
import {
  BENCHMARK_LINE_COLOR,
  rebaseNavPoints,
  type RebasedBenchmarkLine,
} from './navStat';

echarts.use([
  LineChart,
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  TooltipComponent,
  CanvasRenderer,
]);

type NavChartProps = {
  points: API.NavPoint[];
  benchmarks?: API.NavBenchmarkMeta[];
  hiddenKeys?: API.NavBenchmarkKey[];
  onHiddenKeysChange?: (keys: API.NavBenchmarkKey[]) => void;
  height?: number;
  maxNav?: API.NavMaxNavMarker | null;
  drawdown?: API.NavDrawdownPeriod | null;
  showDrawdown?: boolean;
};

const PORTFOLIO_NAME = '净值';

function formatSignedPct(value: number): string {
  const pct = (value - 1) * 100;
  const sign = pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
}

function formatLevel(value: number | null | undefined): string {
  return value != null && Number.isFinite(value) ? value.toFixed(4) : '—';
}

function tooltipHtml(options: {
  date: string;
  compare: boolean;
  portfolio: number | null;
  lines: RebasedBenchmarkLine[];
  index: number;
}): string {
  const { date, compare, portfolio, lines, index } = options;
  const rows = [date, `净值　${formatLevel(portfolio)}${compare && portfolio != null ? `　${formatSignedPct(portfolio)}` : ''}`];
  for (const line of lines) {
    const value = line.values[index];
    if (value == null) {
      rows.push(
        `${line.name}　—${line.sharedAnchor ? '' : '　尚未覆盖'}`,
      );
      continue;
    }
    let extra = '';
    if (compare && line.sharedAnchor && portfolio != null && portfolio !== 0 && value !== 0) {
      const excess = portfolio / value - 1;
      const sign = excess > 0 ? '+' : '';
      extra = `　超额 ${sign}${(excess * 100).toFixed(2)}%`;
    } else if (compare && !line.sharedAnchor && line.startDate) {
      extra = `　自 ${line.startDate} 起`;
    }
    rows.push(`${line.name}　${formatLevel(value)}　${formatSignedPct(value)}${extra}`);
  }
  return rows.join('<br/>');
}

export const NavChart: React.FC<NavChartProps> = ({
  points,
  benchmarks = [],
  hiddenKeys = [],
  onHiddenKeysChange,
  height = 360,
  maxNav = null,
  drawdown = null,
  showDrawdown = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);
  const { token } = theme.useToken();
  const { actualTheme } = useModel('theme');

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = echarts.init(containerRef.current);
    chartRef.current = chart;
    const onResize = () => chart.resize();
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    const dates = points.map((p) => p.date);
    const dateSet = new Set(dates);
    const rebased = rebaseNavPoints(points, benchmarks);
    const hidden = new Set(hiddenKeys);
    const visibleLines = rebased.lines.filter((line) => !hidden.has(line.key));
    const compare = visibleLines.length > 0;
    const portfolioValues = compare
      ? rebased.portfolio
      : points.map((p) => p.navDisplay);

    type MarkLineItem = {
      xAxis: string;
      label?: {
        show?: boolean;
        position?: 'end';
        distance?: number;
        rotate?: number;
        color?: string;
        formatter?: string;
      };
      lineStyle?: {
        type?: 'dashed' | 'solid';
        width?: number;
        color?: string;
      };
    };

    const markData: MarkLineItem[] = [];

    if (maxNav && dateSet.has(maxNav.date) && portfolioValues.length > 1) {
      markData.push({
        xAxis: maxNav.date,
        label: {
          show: true,
          position: 'end',
          distance: 6,
          rotate: 0,
          color: token.colorTextSecondary,
          formatter: `最高 ${Number(maxNav.display).toFixed(4)}`,
        },
        lineStyle: {
          type: 'dashed',
          width: 1,
          color: token.colorWarning,
        },
      });
    }

    if (showDrawdown && drawdown) {
      const ddLabel = {
        show: true,
        position: 'end' as const,
        distance: 6,
        rotate: 0,
        color: token.colorTextSecondary,
      };
      const { peakDate, troughDate, endDate, recovered, recoverDays } = drawdown;
      if (dateSet.has(peakDate)) {
        markData.push({
          xAxis: peakDate,
          label: { ...ddLabel, formatter: '回撤起点' },
          lineStyle: {
            type: 'dashed',
            width: 1,
            color: token.colorError,
          },
        });
      }
      if (dateSet.has(troughDate)) {
        markData.push({
          xAxis: troughDate,
          label: { ...ddLabel, formatter: '最大回撤' },
          lineStyle: {
            type: 'dashed',
            width: 1,
            color: token.colorError,
          },
        });
      }
      if (dateSet.has(endDate)) {
        markData.push({
          xAxis: endDate,
          label: {
            ...ddLabel,
            formatter: recovered
              ? `收复 · ${recoverDays ?? 0}天`
              : '尚未收复',
          },
          lineStyle: {
            type: 'dashed',
            width: 1,
            color: recovered
              ? token.colorError
              : token.colorErrorBorder || token.colorError,
          },
        });
      }
    }

    const markLine =
      markData.length > 0
        ? {
            symbol: 'none' as const,
            silent: true,
            animation: false,
            data: markData,
          }
        : undefined;

    const selected: Record<string, boolean> = { [PORTFOLIO_NAME]: true };
    const legendData: {
      name: string;
      itemStyle: { color: string; borderWidth: number };
      lineStyle: { color: string; width: number };
    }[] = [
      {
        name: PORTFOLIO_NAME,
        itemStyle: { color: token.colorPrimary, borderWidth: 0 },
        lineStyle: { color: token.colorPrimary, width: 2 },
      },
    ];
    for (const line of rebased.lines) {
      selected[line.name] = !hidden.has(line.key);
      const color = BENCHMARK_LINE_COLOR[line.key];
      legendData.push({
        name: line.name,
        itemStyle: { color, borderWidth: 0 },
        lineStyle: { color, width: 2 },
      });
    }

    chart.setOption(
      {
        animation: false,
        backgroundColor: 'transparent',
        grid: { left: 48, right: 16, top: benchmarks.length > 0 ? 64 : 44, bottom: 32 },
        legend: benchmarks.length
          ? {
              top: 0,
              left: 0,
              itemWidth: 22,
              itemHeight: 12,
              textStyle: { color: token.colorTextSecondary, fontSize: 12 },
              data: legendData,
              selected,
            }
          : undefined,
        tooltip: {
          trigger: 'axis',
          formatter: (raw: unknown) => {
            const items = Array.isArray(raw) ? raw : [raw];
            const index = (items[0] as { dataIndex?: number } | undefined)?.dataIndex ?? 0;
            return tooltipHtml({
              date: dates[index] ?? '',
              compare,
              portfolio: portfolioValues[index] ?? null,
              lines: visibleLines,
              index,
            });
          },
        },
        xAxis: {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLine: { lineStyle: { color: token.colorBorderSecondary } },
          axisLabel: { color: token.colorTextSecondary },
        },
        yAxis: {
          type: 'value',
          scale: true,
          splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } },
          axisLabel: {
            color: token.colorTextSecondary,
            formatter: (v: number) => v.toFixed(2),
          },
        },
        series: [
          {
            name: PORTFOLIO_NAME,
            type: 'line',
            data: portfolioValues.map((value) =>
              value != null ? Number(value.toFixed(6)) : null,
            ),
            showSymbol: false,
            smooth: 0.15,
            color: token.colorPrimary,
            itemStyle: { color: token.colorPrimary, borderWidth: 0 },
            lineStyle: { width: 2, color: token.colorPrimary },
            areaStyle: {
              color: token.colorPrimaryBg,
              opacity: 0.45,
            },
            markLine,
          },
          ...rebased.lines.map((line) => ({
            name: line.name,
            type: 'line' as const,
            data: line.values.map((value) =>
              value != null ? Number(value.toFixed(6)) : null,
            ),
            showSymbol: false,
            symbol: 'circle',
            smooth: false,
            connectNulls: false,
            color: BENCHMARK_LINE_COLOR[line.key],
            itemStyle: {
              color: BENCHMARK_LINE_COLOR[line.key],
              borderColor: BENCHMARK_LINE_COLOR[line.key],
              borderWidth: 0,
            },
            lineStyle: {
              width: 1.5,
              type: line.sharedAnchor ? ('solid' as const) : ('dashed' as const),
              color: BENCHMARK_LINE_COLOR[line.key],
            },
          })),
        ],
      },
      true,
    );
    chart.resize();

    const onLegend = (raw: unknown) => {
      const selectedMap = (raw as { selected?: Record<string, boolean> }).selected ?? {};
      const next = rebased.lines
        .filter((line) => selectedMap[line.name] === false)
        .map((line) => line.key);
      onHiddenKeysChange?.(next);
    };
    chart.off('legendselectchanged');
    chart.on('legendselectchanged', onLegend);
    return () => {
      chart.off('legendselectchanged', onLegend);
    };
  }, [
    points,
    benchmarks,
    hiddenKeys,
    onHiddenKeysChange,
    token,
    actualTheme,
    maxNav,
    drawdown,
    showDrawdown,
  ]);

  return <div ref={containerRef} style={{ width: '100%', height }} />;
};
