/**
 * Risk Heatmap Chart Component
 * 
 * Publication-ready heatmap visualization showing barotrauma risk as a
 * function of ET dysfunction severity and descent rate.
 */

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { baseChartOption, colorSchemes, animationConfig } from '../../lib/chartTheme';
import type { HeatmapData } from '../../types/simulation';

interface RiskHeatmapProps {
  data: HeatmapData;
  title?: string;
  height?: number;
  currentPoint?: { x: number; y: string };
}

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({
  data,
  title = 'Risk Heatmap: ET Severity × Descent Rate',
  height = 320,
  currentPoint,
}) => {
  // Transform data for ECharts heatmap format
  const heatmapData = useMemo(() => {
    const result: [number, number, number][] = [];
    data.values.forEach((row, yIdx) => {
      row.forEach((value, xIdx) => {
        result.push([xIdx, yIdx, value]);
      });
    });
    return result;
  }, [data]);

  // Find current point indices
  const currentPointIndices = useMemo(() => {
    if (!currentPoint) return null;
    const xIdx = (data.xLabels as number[]).findIndex(x => x === currentPoint.x);
    const yIdx = data.yLabels.findIndex(y => y.toLowerCase() === currentPoint.y.toLowerCase());
    return xIdx >= 0 && yIdx >= 0 ? { xIdx, yIdx } : null;
  }, [currentPoint, data]);

  const option = useMemo(() => ({
    ...baseChartOption,
    title: {
      ...baseChartOption.title,
      text: title,
      subtext: 'Barotrauma risk score (0-1) across parameters',
    },
    tooltip: {
      ...baseChartOption.tooltip,
      position: 'top',
      formatter: (params: { data: [number, number, number] }) => {
        const [xIdx, yIdx, value] = params.data;
        const severity = data.yLabels[yIdx];
        const rate = data.xLabels[xIdx];
        const riskLevel = value < 0.3 ? 'Low' : value < 0.6 ? 'Moderate' : 'High';
        const color = value < 0.3 ? colorSchemes.risk.low 
          : value < 0.6 ? colorSchemes.risk.moderate 
          : colorSchemes.risk.high;
        
        return `
          <div style="padding: 4px 0;">
            <div style="font-weight: 600; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
              ET Severity: ${severity}
            </div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Descent Rate:</span>
              <span style="font-family: 'JetBrains Mono', monospace;">${rate} ft/min</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Risk Score:</span>
              <span style="font-family: 'JetBrains Mono', monospace; color: ${color};">${value.toFixed(3)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Category:</span>
              <span style="color: ${color}; font-weight: 600;">${riskLevel}</span>
            </div>
          </div>
        `;
      },
    },
    grid: {
      ...baseChartOption.grid,
      top: '18%',
      bottom: '15%',
    },
    xAxis: {
      ...baseChartOption.xAxis,
      type: 'category',
      name: 'Descent Rate (ft/min)',
      data: data.xLabels,
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(255, 255, 255, 0.02)', 'transparent'],
        },
      },
      axisLabel: {
        ...baseChartOption.xAxis.axisLabel,
        interval: Math.floor(data.xLabels.length / 8),
        rotate: 45,
      },
    },
    yAxis: {
      ...baseChartOption.yAxis,
      type: 'category',
      name: 'ET Severity',
      data: data.yLabels,
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(255, 255, 255, 0.02)', 'transparent'],
        },
      },
    },
    visualMap: {
      type: 'continuous',
      min: 0,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: {
        color: colorSchemes.gradients.riskHeatmap.map(g => g.color),
      },
      text: ['High Risk', 'Low Risk'],
      textStyle: {
        color: '#9ca3af',
        fontFamily: 'Inter, sans-serif',
        fontSize: 11,
      },
      itemWidth: 200,
      itemHeight: 12,
    },
    series: [
      {
        type: 'heatmap',
        data: heatmapData,
        label: {
          show: true,
          formatter: (params: { data: [number, number, number] }) => {
            return params.data[2].toFixed(2);
          },
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 10,
          color: (params: { data: [number, number, number] }) => {
            const value = params.data[2];
            return value > 0.5 ? '#fff' : '#000';
          },
        },
        itemStyle: {
          borderColor: 'rgba(0, 0, 0, 0.2)',
          borderWidth: 1,
          borderRadius: 2,
        },
        emphasis: {
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        animationDuration: animationConfig.duration,
        animationEasing: animationConfig.easing,
      },
      // Current point marker
      ...(currentPointIndices ? [{
        type: 'scatter',
        data: [[currentPointIndices.xIdx, currentPointIndices.yIdx]],
        symbol: 'pin',
        symbolSize: 35,
        itemStyle: {
          color: '#fff',
          borderColor: '#0ea5e9',
          borderWidth: 3,
          shadowColor: 'rgba(14, 165, 233, 0.5)',
          shadowBlur: 10,
        },
        z: 10,
        label: {
          show: true,
          position: 'top',
          formatter: 'Current',
          fontFamily: 'Inter, sans-serif',
          fontSize: 10,
          color: '#fff',
          backgroundColor: 'rgba(14, 165, 233, 0.9)',
          padding: [2, 6],
          borderRadius: 3,
        },
      }] : []),
    ],
  }), [data, heatmapData, title, currentPointIndices]);

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default RiskHeatmap;
