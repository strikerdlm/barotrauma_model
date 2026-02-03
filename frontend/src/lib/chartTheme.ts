/**
 * ECharts Theme Configuration
 * 
 * Publication-ready theme for scientific visualization
 * Designed for Q1 journal publication standards and investor presentations
 */

import type { ChartTheme } from '../types/simulation';

export const darkTheme: ChartTheme = {
  backgroundColor: 'transparent',
  textColor: '#e5e7eb',
  axisLineColor: '#374151',
  gridColor: 'rgba(55, 65, 81, 0.3)',
  primaryColor: '#0ea5e9',
  successColor: '#22c55e',
  warningColor: '#eab308',
  dangerColor: '#ef4444',
  gradients: {
    risk: ['#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444'],
    pressure: ['#3b82f6', '#0ea5e9', '#06b6d4', '#14b8a6'],
    altitude: ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef'],
  },
};

/**
 * Base ECharts option for consistent styling across all charts
 */
export const baseChartOption = {
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: 'Inter, system-ui, sans-serif',
    color: '#e5e7eb',
  },
  title: {
    textStyle: {
      fontFamily: 'Outfit, Inter, sans-serif',
      fontWeight: 600,
      fontSize: 16,
      color: '#f9fafb',
    },
    subtextStyle: {
      fontFamily: 'Inter, system-ui, sans-serif',
      fontSize: 12,
      color: '#9ca3af',
    },
  },
  tooltip: {
    backgroundColor: 'rgba(17, 24, 39, 0.95)',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    textStyle: {
      fontFamily: 'Inter, system-ui, sans-serif',
      color: '#f3f4f6',
      fontSize: 12,
    },
    extraCssText: 'box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border-radius: 8px;',
  },
  legend: {
    textStyle: {
      fontFamily: 'Inter, system-ui, sans-serif',
      color: '#d1d5db',
      fontSize: 12,
    },
    icon: 'roundRect',
    itemWidth: 12,
    itemHeight: 12,
    itemGap: 16,
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true,
  },
  xAxis: {
    axisLine: {
      lineStyle: {
        color: '#374151',
      },
    },
    axisTick: {
      lineStyle: {
        color: '#374151',
      },
    },
    axisLabel: {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: 11,
      color: '#9ca3af',
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(55, 65, 81, 0.3)',
        type: 'dashed',
      },
    },
    nameTextStyle: {
      fontFamily: 'Inter, system-ui, sans-serif',
      fontSize: 12,
      color: '#d1d5db',
      padding: [8, 0, 0, 0],
    },
  },
  yAxis: {
    axisLine: {
      lineStyle: {
        color: '#374151',
      },
    },
    axisTick: {
      lineStyle: {
        color: '#374151',
      },
    },
    axisLabel: {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: 11,
      color: '#9ca3af',
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(55, 65, 81, 0.3)',
        type: 'dashed',
      },
    },
    nameTextStyle: {
      fontFamily: 'Inter, system-ui, sans-serif',
      fontSize: 12,
      color: '#d1d5db',
      padding: [0, 0, 8, 0],
    },
  },
};

/**
 * Color schemes for different visualization types
 */
export const colorSchemes = {
  risk: {
    low: '#22c55e',
    lowLight: 'rgba(34, 197, 94, 0.2)',
    moderate: '#eab308',
    moderateLight: 'rgba(234, 179, 8, 0.2)',
    high: '#ef4444',
    highLight: 'rgba(239, 68, 68, 0.2)',
  },
  pressure: {
    ambient: '#3b82f6',
    middleEar: '#10b981',
    differential: '#f59e0b',
    threshold: '#ef4444',
  },
  anatomy: {
    tympanum: '#8b5cf6',
    mastoid: '#ec4899',
    et: '#06b6d4',
  },
  gradients: {
    riskHeatmap: [
      { offset: 0, color: '#22c55e' },
      { offset: 0.3, color: '#84cc16' },
      { offset: 0.5, color: '#eab308' },
      { offset: 0.7, color: '#f97316' },
      { offset: 1, color: '#ef4444' },
    ],
    surface3D: [
      { offset: 0, color: '#06b6d4' },
      { offset: 0.5, color: '#8b5cf6' },
      { offset: 1, color: '#ec4899' },
    ],
    pressure: [
      { offset: 0, color: '#0ea5e9' },
      { offset: 1, color: '#3b82f6' },
    ],
  },
};

/**
 * Animation settings for smooth transitions
 */
export const animationConfig = {
  duration: 800,
  easing: 'cubicOut',
  delay: 0,
  updateDuration: 300,
  updateEasing: 'cubicInOut',
};

/**
 * Mark lines for clinical thresholds
 */
export const thresholdMarkLines = {
  etLock: {
    yAxis: -90,
    lineStyle: {
      color: '#f97316',
      type: 'dashed',
      width: 2,
    },
    label: {
      formatter: 'ET Lock Threshold',
      position: 'insideEndTop',
      color: '#f97316',
      fontFamily: 'Inter, sans-serif',
      fontSize: 11,
    },
  },
  rupture: {
    yAxis: -150,
    lineStyle: {
      color: '#ef4444',
      type: 'dotted',
      width: 2,
    },
    label: {
      formatter: 'Rupture Risk',
      position: 'insideEndTop',
      color: '#ef4444',
      fontFamily: 'Inter, sans-serif',
      fontSize: 11,
    },
  },
};

/**
 * Risk zone areas for charts
 */
export const riskZoneAreas = [
  {
    // Low risk zone
    yAxis: [0, 0.3],
    itemStyle: {
      color: 'rgba(34, 197, 94, 0.1)',
    },
  },
  {
    // Moderate risk zone
    yAxis: [0.3, 0.6],
    itemStyle: {
      color: 'rgba(234, 179, 8, 0.1)',
    },
  },
  {
    // High risk zone
    yAxis: [0.6, 1],
    itemStyle: {
      color: 'rgba(239, 68, 68, 0.1)',
    },
  },
];

/**
 * Export configuration for high-resolution charts
 */
export const exportConfig = {
  pixelRatio: 3,
  backgroundColor: '#0f172a',
  excludeComponents: ['toolbox'],
};
