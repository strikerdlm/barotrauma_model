/**
 * Equalization Dynamics Chart Component
 * 
 * Publication-ready visualization of ET equalization rate and TM displacement
 * during hypobaric chamber descent.
 */

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { baseChartOption, colorSchemes, animationConfig } from '../../lib/chartTheme';
import type { SimulationResult } from '../../types/simulation';

interface EqualizationChartProps {
  result: SimulationResult;
  height?: number;
  mode?: 'rate' | 'displacement' | 'both';
}

export const EqualizationChart: React.FC<EqualizationChartProps> = ({
  result,
  height = 350,
  mode = 'both',
}) => {
  // Convert time to minutes
  const timeMinutes = useMemo(() => 
    result.timeS.map(t => (t / 60).toFixed(2)),
    [result.timeS]
  );

  // Convert displacement to µL for better readability
  const displacementMicroliter = useMemo(() =>
    result.tmDisplacementMl.map(d => (d * 1000).toFixed(2)),
    [result.tmDisplacementMl]
  );

  const option = useMemo(() => ({
    ...baseChartOption,
    title: {
      ...baseChartOption.title,
      text: mode === 'rate' ? 'Equalization Rate Over Time'
        : mode === 'displacement' ? 'Tympanic Membrane Displacement'
        : 'Equalization Dynamics',
      subtext: mode === 'both' 
        ? 'ET function capacity and TM mechanical response'
        : undefined,
    },
    tooltip: {
      ...baseChartOption.tooltip,
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      formatter: (params: { seriesName: string; value: number; axisValue: string }[]) => {
        let html = `<div style="font-weight: 600; margin-bottom: 8px;">Time: ${params[0].axisValue} min</div>`;
        params.forEach(param => {
          const color = param.seriesName.includes('Equalization') 
            ? '#8b5cf6' 
            : '#ec4899';
          const unit = param.seriesName.includes('Equalization') ? 'mmHg/s' : 'µL';
          html += `<div style="display: flex; align-items: center; margin: 4px 0;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 2px; background: ${color}; margin-right: 8px;"></span>
            <span style="flex: 1;">${param.seriesName}</span>
            <span style="font-family: 'JetBrains Mono', monospace; margin-left: 12px;">${parseFloat(param.value.toString()).toFixed(3)} ${unit}</span>
          </div>`;
        });
        return html;
      },
    },
    legend: {
      ...baseChartOption.legend,
      data: mode === 'both' 
        ? ['Equalization Rate', 'TM Displacement']
        : mode === 'rate' 
          ? ['Equalization Rate']
          : ['TM Displacement'],
      top: 40,
    },
    grid: {
      ...baseChartOption.grid,
      top: '18%',
    },
    xAxis: {
      ...baseChartOption.xAxis,
      type: 'category',
      name: 'Time (minutes)',
      data: timeMinutes,
      boundaryGap: false,
      axisLabel: {
        ...baseChartOption.xAxis.axisLabel,
        interval: Math.floor(timeMinutes.length / 8),
      },
    },
    yAxis: mode === 'both' ? [
      {
        ...baseChartOption.yAxis,
        type: 'value',
        name: 'Eq. Rate (mmHg/s)',
        position: 'left',
        axisLine: {
          show: true,
          lineStyle: { color: '#8b5cf6' },
        },
      },
      {
        ...baseChartOption.yAxis,
        type: 'value',
        name: 'Displacement (µL)',
        position: 'right',
        axisLine: {
          show: true,
          lineStyle: { color: '#ec4899' },
        },
        splitLine: { show: false },
      },
    ] : {
      ...baseChartOption.yAxis,
      type: 'value',
      name: mode === 'rate' ? 'Equalization Rate (mmHg/s)' : 'Displacement (µL)',
    },
    series: [
      // Equalization rate
      ...(mode === 'rate' || mode === 'both' ? [{
        name: 'Equalization Rate',
        type: 'line',
        data: result.equalizationRateMmHgS.map(v => v.toFixed(4)),
        smooth: 0.2,
        symbol: 'none',
        yAxisIndex: 0,
        lineStyle: {
          color: '#8b5cf6',
          width: 2.5,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139, 92, 246, 0.4)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0.02)' },
            ],
          },
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 3.5 },
        },
        animationDuration: animationConfig.duration,
      }] : []),
      // TM Displacement
      ...(mode === 'displacement' || mode === 'both' ? [{
        name: 'TM Displacement',
        type: 'line',
        data: displacementMicroliter,
        smooth: 0.2,
        symbol: 'none',
        yAxisIndex: mode === 'both' ? 1 : 0,
        lineStyle: {
          color: '#ec4899',
          width: 2.5,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(236, 72, 153, 0.02)' },
              { offset: 1, color: 'rgba(236, 72, 153, 0.3)' },
            ],
          },
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 3.5 },
        },
        markLine: mode === 'displacement' || mode === 'both' ? {
          silent: true,
          symbol: 'none',
          data: [
            {
              yAxis: 300, // 0.3 mL = 300 µL max physiological limit
              lineStyle: {
                color: '#ef4444',
                type: 'dashed',
                width: 2,
              },
              label: {
                formatter: 'Max Safe Displacement',
                position: 'insideEndTop',
                color: '#ef4444',
                fontFamily: 'Inter, sans-serif',
                fontSize: 10,
              },
            },
          ],
        } : undefined,
        animationDuration: animationConfig.duration,
      }] : []),
    ],
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
    ],
  }), [result, timeMinutes, displacementMicroliter, mode]);

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default EqualizationChart;
