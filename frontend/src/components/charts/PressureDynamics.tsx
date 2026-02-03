/**
 * Pressure Dynamics Chart Component
 * 
 * Publication-ready time series visualization of pressure evolution during
 * hypobaric chamber descent. Shows ambient pressure, middle ear pressure,
 * and pressure differential with clinical threshold annotations.
 */

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { baseChartOption, colorSchemes, animationConfig, thresholdMarkLines } from '../../lib/chartTheme';
import { ET_LOCK_THRESHOLD, MEMBRANE_RUPTURE_THRESHOLD } from '../../lib/simulation';
import type { SimulationResult } from '../../types/simulation';

interface PressureDynamicsProps {
  result: SimulationResult;
  height?: number;
  showDeltaP?: boolean;
}

export const PressureDynamics: React.FC<PressureDynamicsProps> = ({
  result,
  height = 400,
  showDeltaP = true,
}) => {
  // Convert time to minutes for display
  const timeMinutes = useMemo(() => 
    result.timeS.map(t => (t / 60).toFixed(2)),
    [result.timeS]
  );

  const option = useMemo(() => ({
    ...baseChartOption,
    title: {
      ...baseChartOption.title,
      text: 'Pressure Dynamics During Descent',
      subtext: 'Middle ear pressure equalization over time',
    },
    tooltip: {
      ...baseChartOption.tooltip,
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)',
        },
        crossStyle: {
          color: 'rgba(255, 255, 255, 0.3)',
        },
      },
      formatter: (params: { seriesName: string; value: number; axisValue: string }[]) => {
        let html = `<div style="font-weight: 600; margin-bottom: 8px;">Time: ${params[0].axisValue} min</div>`;
        params.forEach(param => {
          const color = param.seriesName === 'Ambient Pressure' ? colorSchemes.pressure.ambient
            : param.seriesName === 'Middle Ear Pressure' ? colorSchemes.pressure.middleEar
            : colorSchemes.pressure.differential;
          html += `<div style="display: flex; align-items: center; margin: 4px 0;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 2px; background: ${color}; margin-right: 8px;"></span>
            <span style="flex: 1;">${param.seriesName}</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-weight: 500; margin-left: 12px;">${param.value.toFixed(1)} mmHg</span>
          </div>`;
        });
        return html;
      },
    },
    legend: {
      ...baseChartOption.legend,
      data: showDeltaP 
        ? ['Ambient Pressure', 'Middle Ear Pressure', 'ΔP (ME - Amb)']
        : ['Ambient Pressure', 'Middle Ear Pressure'],
      top: 40,
    },
    grid: {
      ...baseChartOption.grid,
      top: showDeltaP ? '18%' : '15%',
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
    yAxis: showDeltaP ? [
      {
        ...baseChartOption.yAxis,
        type: 'value',
        name: 'Pressure (mmHg)',
        position: 'left',
        axisLine: {
          show: true,
          lineStyle: { color: colorSchemes.pressure.ambient },
        },
        axisLabel: {
          ...baseChartOption.yAxis.axisLabel,
          formatter: '{value}',
        },
      },
      {
        ...baseChartOption.yAxis,
        type: 'value',
        name: 'ΔP (mmHg)',
        position: 'right',
        axisLine: {
          show: true,
          lineStyle: { color: colorSchemes.pressure.differential },
        },
        splitLine: { show: false },
      },
    ] : {
      ...baseChartOption.yAxis,
      type: 'value',
      name: 'Pressure (mmHg)',
    },
    series: [
      {
        name: 'Ambient Pressure',
        type: 'line',
        data: result.pAmbMmHg.map(v => v.toFixed(2)),
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: colorSchemes.pressure.ambient,
          width: 3,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.02)' },
            ],
          },
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 4 },
        },
        animationDuration: animationConfig.duration,
      },
      {
        name: 'Middle Ear Pressure',
        type: 'line',
        data: result.pMeMmHg.map(v => v.toFixed(2)),
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: colorSchemes.pressure.middleEar,
          width: 3,
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 4 },
        },
        animationDuration: animationConfig.duration,
      },
      ...(showDeltaP ? [{
        name: 'ΔP (ME - Amb)',
        type: 'line',
        yAxisIndex: 1,
        data: result.deltaPMmHg.map(v => v.toFixed(2)),
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: colorSchemes.pressure.differential,
          width: 2,
          type: 'dashed',
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 158, 11, 0.02)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.2)' },
            ],
          },
        },
        markLine: {
          silent: true,
          symbol: 'none',
          data: [
            {
              ...thresholdMarkLines.etLock,
              label: {
                ...thresholdMarkLines.etLock.label,
                position: 'insideStartTop',
              },
            },
            thresholdMarkLines.rupture,
          ],
        },
        markArea: {
          silent: true,
          data: [
            [
              { yAxis: -ET_LOCK_THRESHOLD, itemStyle: { color: 'rgba(249, 115, 22, 0.1)' } },
              { yAxis: -MEMBRANE_RUPTURE_THRESHOLD },
            ],
            [
              { yAxis: -MEMBRANE_RUPTURE_THRESHOLD, itemStyle: { color: 'rgba(239, 68, 68, 0.15)' } },
              { yAxis: -200 },
            ],
          ],
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 3 },
        },
        animationDuration: animationConfig.duration,
      }] : []),
    ],
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
        xAxisIndex: 0,
      },
      {
        type: 'slider',
        show: true,
        xAxisIndex: 0,
        start: 0,
        end: 100,
        height: 20,
        bottom: 0,
        borderColor: 'transparent',
        backgroundColor: 'rgba(55, 65, 81, 0.3)',
        fillerColor: 'rgba(14, 165, 233, 0.2)',
        handleStyle: {
          color: '#0ea5e9',
          borderColor: '#0ea5e9',
        },
        textStyle: {
          color: '#9ca3af',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 10,
        },
      },
    ],
  }), [result, timeMinutes, showDeltaP]);

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default PressureDynamics;
