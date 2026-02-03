/**
 * Risk Gauge Chart Component
 * 
 * Publication-ready gauge visualization for barotrauma risk score display.
 * Features smooth animations, threshold markers, and clinical color coding.
 */

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { baseChartOption, colorSchemes, animationConfig } from '../../lib/chartTheme';
import type { RiskCategory } from '../../types/simulation';

interface RiskGaugeProps {
  riskScore: number;
  riskCategory: RiskCategory;
  title?: string;
  height?: number;
  showAnimation?: boolean;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  riskScore,
  riskCategory,
  title = 'Risk Score',
  height = 280,
  showAnimation = true,
}) => {
  const option = useMemo(() => ({
    ...baseChartOption,
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 1,
        splitNumber: 10,
        itemStyle: {
          color: riskScore < 0.3 
            ? colorSchemes.risk.low 
            : riskScore < 0.6 
              ? colorSchemes.risk.moderate 
              : colorSchemes.risk.high,
          shadowColor: riskScore < 0.3 
            ? 'rgba(34, 197, 94, 0.5)' 
            : riskScore < 0.6 
              ? 'rgba(234, 179, 8, 0.5)' 
              : 'rgba(239, 68, 68, 0.5)',
          shadowBlur: 10,
        },
        progress: {
          show: true,
          width: 18,
          roundCap: true,
        },
        pointer: {
          icon: 'path://M2090.36389,615.30999 L2## 90.36389,615.30999 C2## 91.48372,615.30999 2## 92.40925,616.194028 2## 92.40925,617.28846 L2## 92.40925,1077.58498 C2## 92.40925,1## 078.6## 794 2## 91.48372,1## 079.56451 2## 90.36389,1## 079.56451 L2## 90.36389,1## 079.56451 C2## 89.24052,1## 079.56451 2## 88.31499,1## 078.6## 794 2## 88.31499,1077.58498 L2## 88.31499,617.28846 C2## 88.31499,616.194028 2## 89.24052,615.30999 2## 90.36389,615.30999 Z',
          length: '75%',
          width: 8,
          offsetCenter: [0, '5%'],
          itemStyle: {
            color: '#f9fafb',
            shadowColor: 'rgba(249, 250, 251, 0.3)',
            shadowBlur: 6,
          },
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 18,
            color: [
              [0.3, colorSchemes.risk.low],
              [0.6, colorSchemes.risk.moderate],
              [1, colorSchemes.risk.high],
            ],
            shadowColor: 'rgba(0, 0, 0, 0.2)',
            shadowBlur: 8,
          },
        },
        axisTick: {
          distance: -32,
          splitNumber: 5,
          lineStyle: {
            width: 2,
            color: '#374151',
          },
        },
        splitLine: {
          distance: -38,
          length: 14,
          lineStyle: {
            width: 3,
            color: '#4b5563',
          },
        },
        axisLabel: {
          distance: -24,
          color: '#9ca3af',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 10,
          formatter: (value: number) => {
            if (value === 0) return 'Safe';
            if (value === 0.5) return '';
            if (value === 1) return 'Critical';
            return '';
          },
        },
        anchor: {
          show: true,
          showAbove: true,
          size: 20,
          itemStyle: {
            borderWidth: 8,
            borderColor: riskScore < 0.3 
              ? colorSchemes.risk.low 
              : riskScore < 0.6 
                ? colorSchemes.risk.moderate 
                : colorSchemes.risk.high,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
            shadowBlur: 10,
          },
        },
        title: {
          show: true,
          offsetCenter: [0, '90%'],
          fontSize: 14,
          fontFamily: 'Outfit, Inter, sans-serif',
          fontWeight: 500,
          color: '#9ca3af',
        },
        detail: {
          valueAnimation: showAnimation,
          fontSize: 36,
          fontFamily: 'JetBrains Mono, monospace',
          fontWeight: 600,
          offsetCenter: [0, '55%'],
          formatter: (value: number) => (value * 100).toFixed(0) + '%',
          color: riskScore < 0.3 
            ? colorSchemes.risk.low 
            : riskScore < 0.6 
              ? colorSchemes.risk.moderate 
              : colorSchemes.risk.high,
        },
        data: [
          {
            value: riskScore,
            name: riskCategory,
          },
        ],
        animation: showAnimation,
        animationDuration: animationConfig.duration,
        animationEasing: animationConfig.easing,
      },
      // Background ring
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 1,
        z: 0,
        progress: {
          show: false,
        },
        pointer: {
          show: false,
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 18,
            color: [
              [1, 'rgba(55, 65, 81, 0.4)'],
            ],
          },
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: { show: false },
      },
    ],
  }), [riskScore, riskCategory, showAnimation]);

  return (
    <div className="relative">
      <div className="absolute top-2 left-1/2 -translate-x-1/2 text-center">
        <span className="text-sm font-medium text-gray-400">{title}</span>
      </div>
      <ReactECharts
        option={option}
        style={{ height: `${height}px`, width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </div>
  );
};

export default RiskGauge;
