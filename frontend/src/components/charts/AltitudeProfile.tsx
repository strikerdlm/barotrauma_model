/**
 * Altitude Profile Chart Component
 * 
 * Publication-ready visualization showing altitude descent profile
 * with associated risk factor overlay.
 */

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { baseChartOption, colorSchemes, animationConfig } from '../../lib/chartTheme';
import type { SimulationResult } from '../../types/simulation';

interface AltitudeProfileProps {
  result: SimulationResult;
  height?: number;
  showRisk?: boolean;
}

export const AltitudeProfile: React.FC<AltitudeProfileProps> = ({
  result,
  height = 300,
  showRisk = true,
}) => {
  // Convert time to minutes
  const timeMinutes = useMemo(() => 
    result.timeS.map(t => (t / 60).toFixed(2)),
    [result.timeS]
  );

  // Calculate instantaneous risk based on delta P
  const instantaneousRisk = useMemo(() => {
    const maxDeltaP = 150; // mmHg for normalization
    return result.deltaPMmHg.map(dp => {
      const normalized = Math.min(Math.abs(dp) / maxDeltaP, 1);
      return normalized.toFixed(3);
    });
  }, [result.deltaPMmHg]);

  const option = useMemo(() => ({
    ...baseChartOption,
    title: {
      ...baseChartOption.title,
      text: 'Altitude & Risk Profile',
      subtext: 'Descent profile with instantaneous risk indication',
    },
    tooltip: {
      ...baseChartOption.tooltip,
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)',
        },
      },
      formatter: (params: { seriesName: string; value: number; axisValue: string }[]) => {
        let html = `<div style="font-weight: 600; margin-bottom: 8px;">Time: ${params[0].axisValue} min</div>`;
        params.forEach(param => {
          if (param.seriesName === 'Altitude') {
            html += `<div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Altitude:</span>
              <span style="font-family: 'JetBrains Mono', monospace;">${parseFloat(param.value.toString()).toFixed(0)} ft</span>
            </div>`;
          } else if (param.seriesName === 'Risk Factor') {
            const risk = parseFloat(param.value.toString());
            const riskLevel = risk < 0.3 ? 'Low' : risk < 0.6 ? 'Moderate' : 'High';
            const color = risk < 0.3 ? colorSchemes.risk.low 
              : risk < 0.6 ? colorSchemes.risk.moderate 
              : colorSchemes.risk.high;
            html += `<div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Instant Risk:</span>
              <span style="font-family: 'JetBrains Mono', monospace; color: ${color};">${(risk * 100).toFixed(1)}%</span>
            </div>
            <div style="text-align: center; margin-top: 4px;">
              <span style="background: ${color}20; color: ${color}; padding: 2px 8px; border-radius: 4px; font-size: 10px;">${riskLevel}</span>
            </div>`;
          }
        });
        return html;
      },
    },
    legend: {
      ...baseChartOption.legend,
      data: showRisk ? ['Altitude', 'Risk Factor'] : ['Altitude'],
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
    yAxis: showRisk ? [
      {
        ...baseChartOption.yAxis,
        type: 'value',
        name: 'Altitude (ft)',
        position: 'left',
        axisLine: {
          show: true,
          lineStyle: { color: '#6366f1' },
        },
      },
      {
        ...baseChartOption.yAxis,
        type: 'value',
        name: 'Risk Factor',
        position: 'right',
        min: 0,
        max: 1,
        axisLine: {
          show: true,
          lineStyle: { color: '#ef4444' },
        },
        splitLine: { show: false },
      },
    ] : {
      ...baseChartOption.yAxis,
      type: 'value',
      name: 'Altitude (ft)',
    },
    series: [
      // Altitude profile
      {
        name: 'Altitude',
        type: 'line',
        data: result.altitudeFt,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: '#6366f1',
          width: 3,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(99, 102, 241, 0.4)' },
              { offset: 0.5, color: 'rgba(99, 102, 241, 0.15)' },
              { offset: 1, color: 'rgba(99, 102, 241, 0.02)' },
            ],
          },
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 4 },
        },
        animationDuration: animationConfig.duration,
      },
      // Risk factor overlay
      ...(showRisk ? [{
        name: 'Risk Factor',
        type: 'line',
        yAxisIndex: 1,
        data: instantaneousRisk,
        smooth: 0.3,
        symbol: 'none',
        lineStyle: {
          color: '#ef4444',
          width: 2,
          type: 'dashed',
        },
        emphasis: {
          focus: 'series',
          lineStyle: { width: 3 },
        },
        markLine: {
          silent: true,
          symbol: 'none',
          data: [
            {
              yAxis: 0.3,
              lineStyle: {
                color: colorSchemes.risk.moderate,
                type: 'dotted',
                width: 1,
              },
              label: {
                formatter: 'Moderate',
                position: 'insideEndTop',
                color: colorSchemes.risk.moderate,
                fontSize: 9,
              },
            },
            {
              yAxis: 0.6,
              lineStyle: {
                color: colorSchemes.risk.high,
                type: 'dotted',
                width: 1,
              },
              label: {
                formatter: 'High',
                position: 'insideEndTop',
                color: colorSchemes.risk.high,
                fontSize: 9,
              },
            },
          ],
        },
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
  }), [result, timeMinutes, instantaneousRisk, showRisk]);

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default AltitudeProfile;
