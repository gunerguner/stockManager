import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { theme } from 'antd';
import { useModel } from '@umijs/max';

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

type NavChartProps = {
  points: API.NavPoint[];
  height?: number;
};

export const NavChart: React.FC<NavChartProps> = ({ points, height = 360 }) => {
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

    chart.setOption(
      {
        backgroundColor: 'transparent',
        grid: { left: 48, right: 24, top: 24, bottom: 32 },
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
          },
        ],
      },
      true,
    );
    chart.resize();
  }, [points, token, actualTheme]);

  return <div ref={containerRef} style={{ width: '100%', height }} />;
};
