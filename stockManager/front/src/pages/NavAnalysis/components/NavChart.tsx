import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import {
  GridComponent,
  MarkLineComponent,
  TooltipComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { theme } from 'antd';
import { useModel } from '@umijs/max';

echarts.use([
  LineChart,
  GridComponent,
  MarkLineComponent,
  TooltipComponent,
  CanvasRenderer,
]);

type NavChartProps = {
  points: API.NavPoint[];
  height?: number;
  maxNav?: API.NavMaxNavMarker | null;
  drawdown?: API.NavDrawdownPeriod | null;
  showDrawdown?: boolean;
};

export const NavChart: React.FC<NavChartProps> = ({
  points,
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
    const values = points.map((p) => Number(p.navDisplay.toFixed(6)));
    const dateSet = new Set(dates);

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

    if (maxNav && dateSet.has(maxNav.date) && values.length > 1) {
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

    chart.setOption(
      {
        animation: false,
        backgroundColor: 'transparent',
        grid: { left: 48, right: 24, top: 44, bottom: 32 },
        tooltip: {
          trigger: 'axis',
          valueFormatter: (v: number) => (v != null ? Number(v).toFixed(4) : '—'),
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
            name: '净值',
            type: 'line',
            data: values,
            showSymbol: false,
            smooth: 0.15,
            lineStyle: { width: 2, color: token.colorPrimary },
            areaStyle: {
              color: token.colorPrimaryBg,
              opacity: 0.45,
            },
            markLine,
          },
        ],
      },
      true,
    );
    chart.resize();
  }, [points, token, actualTheme, maxNav, drawdown, showDrawdown]);

  return <div ref={containerRef} style={{ width: '100%', height }} />;
};
