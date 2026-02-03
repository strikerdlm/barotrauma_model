/**
 * Sensitivity Analysis Chart Component
 * 
 * Publication-ready visualization showing risk sensitivity to descent rate
 * with risk zone highlighting and current position marker.
 */

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { baseChartOption, colorSchemes, animationConfig } from '../../lib/chartTheme';
import type { SensitivityPoint } from '../../types/simulation';

interface SensitivityAnalysisProps {
  data: SensitivityPoint[];
  currentRate?: number;
  currentRisk?: number;
  title?: string;
  height?: number;
}

export const SensitivityAnalysis: React.FC<SensitivityAnalysisProps> = ({
  data,
  currentRate,
  currentRisk,
  title = 'Risk Score vs Descent Rate',
  height = 380,
}) => {
  const option = useMemo(() => ({
    ...baseChartOption,
    title: {
      ...baseChartOption.title,
      text: title,
      subtext: 'Sensitivity analysis showing risk response to descent rate changes',
    },
    tooltip: {
      ...baseChartOption.tooltip,
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: 'rgba(17, 24, 39, 0.95)',
          fontFamily: 'JetBrains Mono, monospace',
        },
      },
      formatter: (params: { value: number; axisValue: number }[]) => {
        const rate = params[0].axisValue;
        const risk = params[0].value;
        const riskLevel = risk < 0.3 ? 'Low' : risk < 0.6 ? 'Moderate' : 'High';
        const color = risk < 0.3 ? colorSchemes.risk.low 
          : risk < 0.6 ? colorSchemes.risk.moderate 
          : colorSchemes.risk.high;
        
        return `
          <div style="padding: 4px 0;">
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Descent Rate:</span>
              <span style="font-family: 'JetBrains Mono', monospace;">${rate.toFixed(0)} ft/min</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Risk Score:</span>
              <span style="font-family: 'JetBrains Mono', monospace; color: ${color};">${risk.toFixed(3)}</span>
            </div>
            <div style="text-align: center; margin-top: 8px;">
              <span style="background: ${color}20; color: ${color}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">${riskLevel} Risk</span>
            </div>
          </div>
        `;
      },
    },
    legend: {
      ...baseChartOption.legend,
      data: ['Risk Score', 'Current Setting'],
      top: 40,
    },
    grid: {
      ...baseChartOption.grid,
      top: '18%',
    },
    xAxis: {
      ...baseChartOption.xAxis,
      type: 'value',
      name: 'Descent Rate (ft/min)',
      min: Math.min(...data.map(d => d.parameterValue)),
      max: Math.max(...data.map(d => d.parameterValue)),
    },
    yAxis: {
      ...baseChartOption.yAxis,
      type: 'value',
      name: 'Risk Score',
      min: 0,
      max: 1,
      interval: 0.2,
    },
    series: [
      // Risk zones as area backgrounds
      {
        type: 'line',
        data: [],
        markArea: {
          silent: true,
          data: [
            [
              {
                yAxis: 0,
                itemStyle: {
                  color: {
                    type: 'linear',
                    x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                      { offset: 0, color: 'rgba(34, 197, 94, 0.25)' },
                      { offset: 1, color: 'rgba(34, 197, 94, 0.05)' },
                    ],
                  },
                },
              },
              { yAxis: 0.3 },
            ],
            [
              {
                yAxis: 0.3,
                itemStyle: {
                  color: {
                    type: 'linear',
                    x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                      { offset: 0, color: 'rgba(234, 179, 8, 0.25)' },
                      { offset: 1, color: 'rgba(234, 179, 8, 0.05)' },
                    ],
                  },
                },
              },
              { yAxis: 0.6 },
            ],
            [
              {
                yAxis: 0.6,
                itemStyle: {
                  color: {
                    type: 'linear',
                    x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                      { offset: 0, color: 'rgba(239, 68, 68, 0.25)' },
                      { offset: 1, color: 'rgba(239, 68, 68, 0.05)' },
                    ],
                  },
                },
              },
              { yAxis: 1 },
            ],
          ],
        },
      },
      // Zone labels
      {
        type: 'line',
        data: [],
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { opacity: 0 },
          label: {
            show: true,
            position: 'insideEndTop',
            fontFamily: 'Inter, sans-serif',
            fontSize: 10,
          },
          data: [
            {
              yAxis: 0.15,
              label: {
                formatter: 'Low Risk Zone',
                color: colorSchemes.risk.low,
              },
            },
            {
              yAxis: 0.45,
              label: {
                formatter: 'Moderate Risk Zone',
                color: colorSchemes.risk.moderate,
              },
            },
            {
              yAxis: 0.8,
              label: {
                formatter: 'High Risk Zone',
                color: colorSchemes.risk.high,
              },
            },
          ],
        },
      },
      // Main risk line
      {
        name: 'Risk Score',
        type: 'line',
        data: data.map(d => [d.parameterValue, d.riskScore]),
        smooth: 0.3,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#0ea5e9',
          width: 3,
          shadowColor: 'rgba(14, 165, 233, 0.4)',
          shadowBlur: 8,
        },
        itemStyle: {
          color: '#0ea5e9',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(14, 165, 233, 0.4)' },
              { offset: 1, color: 'rgba(14, 165, 233, 0.02)' },
            ],
          },
        },
        emphasis: {
          scale: true,
          itemStyle: {
            shadowBlur: 15,
            shadowColor: 'rgba(14, 165, 233, 0.6)',
          },
        },
        animationDuration: animationConfig.duration,
        animationEasing: animationConfig.easing,
      },
      // Current position marker
      ...(currentRate !== undefined && currentRisk !== undefined ? [{
        name: 'Current Setting',
        type: 'scatter',
        data: [[currentRate, currentRisk]],
        symbol: 'pin',
        symbolSize: 50,
        symbolOffset: [0, '-40%'],
        itemStyle: {
          color: '#fbbf24',
          shadowColor: 'rgba(251, 191, 36, 0.5)',
          shadowBlur: 15,
        },
        label: {
          show: true,
          position: 'top',
          distance: 10,
          formatter: (params: { value: [number, number] }) => {
            return `Current: ${params.value[1].toFixed(2)}`;
          },
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11,
          color: '#fbbf24',
          backgroundColor: 'rgba(251, 191, 36, 0.15)',
          padding: [4, 8],
          borderRadius: 4,
        },
        z: 10,
      }] : []),
    ],
  }), [data, title, currentRate, currentRisk]);

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default SensitivityAnalysis;
