/**
 * 3D Risk Surface Chart Component
 * 
 * Publication-ready 3D surface visualization showing barotrauma risk
 * as a function of ET dysfunction and descent rate.
 * Uses ECharts-GL for hardware-accelerated 3D rendering.
 */

import React, { useMemo, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';
import 'echarts-gl';
import { baseChartOption, colorSchemes, animationConfig } from '../../lib/chartTheme';

interface RiskSurface3DProps {
  surfaceData: {
    x: number[];
    y: number[];
    z: number[][];
  };
  title?: string;
  height?: number;
  currentPoint?: { et: number; rate: number; risk: number };
}

export const RiskSurface3D: React.FC<RiskSurface3DProps> = ({
  surfaceData,
  title = '3D Risk Surface: ET Dysfunction × Descent Rate',
  height = 500,
  currentPoint,
}) => {
  // Transform data for surface series
  const surfaceSeriesData = useMemo(() => {
    const data: number[][] = [];
    surfaceData.y.forEach((rate, rateIdx) => {
      surfaceData.x.forEach((et, etIdx) => {
        data.push([et, rate, surfaceData.z[rateIdx][etIdx]]);
      });
    });
    return data;
  }, [surfaceData]);

  // Generate threshold plane data
  const thresholdPlaneData = (threshold: number) => {
    const data: number[][] = [];
    const etMin = Math.min(...surfaceData.x);
    const etMax = Math.max(...surfaceData.x);
    const rateMin = Math.min(...surfaceData.y);
    const rateMax = Math.max(...surfaceData.y);
    
    for (let i = 0; i < 10; i++) {
      for (let j = 0; j < 10; j++) {
        const et = etMin + (etMax - etMin) * (i / 9);
        const rate = rateMin + (rateMax - rateMin) * (j / 9);
        data.push([et, rate, threshold]);
      }
    }
    return data;
  };

  const option = useMemo(() => ({
    backgroundColor: 'transparent',
    title: {
      ...baseChartOption.title,
      text: title,
      subtext: 'Interactive 3D visualization - click and drag to rotate',
      left: 'center',
    },
    tooltip: {
      ...baseChartOption.tooltip,
      formatter: (params: { data: number[] }) => {
        if (!params.data) return '';
        const [et, rate, risk] = params.data;
        const riskLevel = risk < 0.3 ? 'Low' : risk < 0.6 ? 'Moderate' : 'High';
        const color = risk < 0.3 ? colorSchemes.risk.low 
          : risk < 0.6 ? colorSchemes.risk.moderate 
          : colorSchemes.risk.high;
        
        return `
          <div style="padding: 4px 0;">
            <div style="font-weight: 600; margin-bottom: 8px;">Risk Analysis Point</div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">ET Dysfunction:</span>
              <span style="font-family: 'JetBrains Mono', monospace;">${(et * 100).toFixed(0)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0;">
              <span style="color: #9ca3af;">Descent Rate:</span>
              <span style="font-family: 'JetBrains Mono', monospace;">${rate.toFixed(0)} ft/min</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 4px 0; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.1);">
              <span style="color: #9ca3af;">Risk Score:</span>
              <span style="font-family: 'JetBrains Mono', monospace; color: ${color}; font-weight: 600;">${risk.toFixed(3)}</span>
            </div>
            <div style="text-align: center; margin-top: 8px;">
              <span style="background: ${color}20; color: ${color}; padding: 2px 8px; border-radius: 4px; font-size: 11px;">${riskLevel} Risk</span>
            </div>
          </div>
        `;
      },
    },
    visualMap: {
      show: true,
      dimension: 2,
      min: 0,
      max: 1,
      inRange: {
        color: colorSchemes.gradients.riskHeatmap.map(g => g.color),
      },
      text: ['High', 'Low'],
      textStyle: {
        color: '#9ca3af',
        fontFamily: 'Inter, sans-serif',
        fontSize: 11,
      },
      left: 30,
      top: 'middle',
      itemHeight: 200,
    },
    xAxis3D: {
      type: 'value',
      name: 'ET Dysfunction',
      min: 0,
      max: 1,
      nameTextStyle: {
        color: '#d1d5db',
        fontFamily: 'Inter, sans-serif',
        fontSize: 12,
      },
      axisLabel: {
        formatter: (value: number) => `${(value * 100).toFixed(0)}%`,
        color: '#9ca3af',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: 10,
      },
      axisLine: {
        lineStyle: { color: '#4b5563' },
      },
      splitLine: {
        lineStyle: { color: 'rgba(75, 85, 99, 0.3)' },
      },
    },
    yAxis3D: {
      type: 'value',
      name: 'Descent Rate (ft/min)',
      nameTextStyle: {
        color: '#d1d5db',
        fontFamily: 'Inter, sans-serif',
        fontSize: 12,
      },
      axisLabel: {
        color: '#9ca3af',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: 10,
      },
      axisLine: {
        lineStyle: { color: '#4b5563' },
      },
      splitLine: {
        lineStyle: { color: 'rgba(75, 85, 99, 0.3)' },
      },
    },
    zAxis3D: {
      type: 'value',
      name: 'Risk Score',
      min: 0,
      max: 1,
      nameTextStyle: {
        color: '#d1d5db',
        fontFamily: 'Inter, sans-serif',
        fontSize: 12,
      },
      axisLabel: {
        color: '#9ca3af',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: 10,
      },
      axisLine: {
        lineStyle: { color: '#4b5563' },
      },
      splitLine: {
        lineStyle: { color: 'rgba(75, 85, 99, 0.3)' },
      },
    },
    grid3D: {
      viewControl: {
        autoRotate: false,
        autoRotateSpeed: 5,
        distance: 180,
        alpha: 25,
        beta: 35,
        rotateSensitivity: 1,
        zoomSensitivity: 1,
        panSensitivity: 1,
      },
      boxWidth: 100,
      boxHeight: 60,
      boxDepth: 100,
      environment: 'auto',
      light: {
        main: {
          intensity: 1.2,
          shadow: true,
          shadowQuality: 'high',
        },
        ambient: {
          intensity: 0.4,
        },
      },
      postEffect: {
        enable: true,
        bloom: {
          enable: true,
          intensity: 0.1,
        },
        SSAO: {
          enable: true,
          radius: 2,
          intensity: 1.5,
        },
      },
    },
    series: [
      // Main risk surface
      {
        type: 'surface',
        wireframe: {
          show: false,
        },
        shading: 'realistic',
        realisticMaterial: {
          roughness: 0.5,
          metalness: 0.1,
        },
        itemStyle: {
          opacity: 0.95,
        },
        data: surfaceSeriesData,
      },
      // Moderate risk threshold plane (0.3)
      {
        type: 'surface',
        wireframe: {
          show: true,
          lineStyle: {
            color: 'rgba(234, 179, 8, 0.3)',
            width: 1,
          },
        },
        shading: 'color',
        itemStyle: {
          color: 'rgba(234, 179, 8, 0.15)',
          opacity: 0.3,
        },
        data: thresholdPlaneData(0.3),
        silent: true,
      },
      // High risk threshold plane (0.6)
      {
        type: 'surface',
        wireframe: {
          show: true,
          lineStyle: {
            color: 'rgba(239, 68, 68, 0.3)',
            width: 1,
          },
        },
        shading: 'color',
        itemStyle: {
          color: 'rgba(239, 68, 68, 0.15)',
          opacity: 0.3,
        },
        data: thresholdPlaneData(0.6),
        silent: true,
      },
      // Current point marker
      ...(currentPoint ? [{
        type: 'scatter3D',
        symbolSize: 15,
        data: [[currentPoint.et, currentPoint.rate, currentPoint.risk]],
        itemStyle: {
          color: '#fff',
          borderColor: '#0ea5e9',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(14, 165, 233, 0.8)',
        },
        label: {
          show: true,
          formatter: 'Current',
          color: '#fff',
          fontSize: 11,
          fontFamily: 'Inter, sans-serif',
          backgroundColor: 'rgba(14, 165, 233, 0.9)',
          padding: [3, 8],
          borderRadius: 4,
        },
      }] : []),
    ],
  }), [surfaceSeriesData, title, currentPoint]);

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default RiskSurface3D;
