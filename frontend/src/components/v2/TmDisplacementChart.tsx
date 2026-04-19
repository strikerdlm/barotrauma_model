/**
 * TmDisplacementChart — tympanic-membrane volume-displacement trace.
 *
 * Renders the ``tm_displacement_ml`` array returned by the Python engine.
 * Displayed in microliters (× 1000 for readability). The TM has a bounded
 * compliance: under Kanick-Doyle / Doyle 2011 the saturation clamp is
 * ±0.025 mL (±25 µL) at ~1% of V_ME. Those bounds are rendered as dashed
 * mark lines so a reviewer can see when the TM is against the stop vs.
 * operating in its compliant range.
 *
 * No physics here — all arrays come from ``trace`` on the simulate
 * response. Rendering only.
 */

import ReactECharts from 'echarts-for-react';
import { useMemo } from 'react';

import { baseChartOption, colorSchemes } from '../../lib/chartTheme';
import type { SimulationTraceV2 } from '../../types/v2';

interface TmDisplacementChartProps {
  trace: SimulationTraceV2 | null;
  height?: number;
  loading?: boolean;
}

const TM_SATURATION_UL = 25.0;

export function TmDisplacementChart({
  trace,
  height = 360,
  loading = false,
}: TmDisplacementChartProps) {
  const option = useMemo(() => {
    if (!trace) return null;

    const tMinutes = trace.t_s.map((t) => t / 60);
    // µL for readability — native ml is ~1e-3 scale
    const tmDisplacementUl = trace.tm_displacement_ml.map((v) => v * 1000);
    const tmSeries = tmDisplacementUl.map((v, i) => [tMinutes[i], v]);
    const deltaPSeries = trace.delta_p_mmHg.map((dp, i) => [tMinutes[i], dp]);

    const peak = tmDisplacementUl.reduce((m, v) => Math.max(m, Math.abs(v)), 0);
    const yMax = Math.max(TM_SATURATION_UL * 1.1, Math.ceil(peak * 1.1));

    return {
      ...baseChartOption,
      title: {
        ...baseChartOption.title,
        text: 'Tympanic-membrane displacement',
        subtext:
          'TM volume excursion (left, µL) vs. middle-ear ΔP (right, mmHg). Clamp ±25 µL (Doyle 2011) shown dashed.',
        top: 8,
        left: 12,
      },
      legend: {
        ...baseChartOption.legend,
        data: ['TM displacement', 'ΔP (P_ME − P_ambient)'],
        top: 44,
        right: 16,
      },
      grid: {
        ...baseChartOption.grid,
        top: 96,
        left: 64,
        right: 72,
        bottom: 72,
        containLabel: false,
      },
      tooltip: {
        ...baseChartOption.tooltip,
        trigger: 'axis',
        axisPointer: { type: 'cross', snap: true },
        valueFormatter: (v: number) => (typeof v === 'number' ? v.toFixed(2) : '—'),
      },
      xAxis: {
        ...baseChartOption.xAxis,
        type: 'value',
        name: 'Time (min)',
        nameLocation: 'middle',
        nameGap: 30,
        min: 0,
        max: Math.max(...tMinutes),
      },
      yAxis: [
        {
          ...baseChartOption.yAxis,
          type: 'value',
          name: 'TM displacement (µL)',
          position: 'left',
          nameGap: 48,
          nameLocation: 'middle',
          min: -yMax,
          max: yMax,
          axisLine: {
            show: true,
            lineStyle: { color: colorSchemes.anatomy.tympanum },
          },
        },
        {
          ...baseChartOption.yAxis,
          type: 'value',
          name: 'ΔP (mmHg)',
          position: 'right',
          nameGap: 40,
          nameLocation: 'middle',
          axisLine: {
            show: true,
            lineStyle: { color: colorSchemes.pressure.differential },
          },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: 'TM displacement',
          type: 'line',
          yAxisIndex: 0,
          data: tmSeries,
          smooth: false,
          symbol: 'none',
          lineStyle: { color: colorSchemes.anatomy.tympanum, width: 2 },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(139, 92, 246, 0.25)' },
                { offset: 0.5, color: 'rgba(139, 92, 246, 0.02)' },
                { offset: 1, color: 'rgba(139, 92, 246, 0.25)' },
              ],
            },
            origin: 'start',
          },
          z: 2,
          markLine: {
            silent: true,
            symbol: 'none',
            lineStyle: { type: 'dashed', width: 1 },
            label: {
              formatter: '{b}',
              position: 'insideStartTop',
              color: '#9ca3af',
              fontSize: 10,
            },
            data: [
              {
                name: 'TM clamp +25 µL',
                yAxis: TM_SATURATION_UL,
                lineStyle: { color: colorSchemes.risk.high },
              },
              {
                name: 'TM clamp −25 µL',
                yAxis: -TM_SATURATION_UL,
                lineStyle: { color: colorSchemes.risk.high },
              },
              {
                name: 'zero',
                yAxis: 0,
                lineStyle: { color: 'rgba(156, 163, 175, 0.5)', type: 'solid' },
                label: { show: false },
              },
            ],
          },
        },
        {
          name: 'ΔP (P_ME − P_ambient)',
          type: 'line',
          yAxisIndex: 1,
          data: deltaPSeries,
          smooth: false,
          symbol: 'none',
          lineStyle: {
            color: colorSchemes.pressure.differential,
            width: 1.5,
            opacity: 0.7,
          },
          z: 1,
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: 0,
          start: 0,
          end: 100,
        },
        {
          type: 'slider',
          xAxisIndex: 0,
          height: 18,
          bottom: 16,
          start: 0,
          end: 100,
          borderColor: 'transparent',
          backgroundColor: 'rgba(17, 24, 39, 0.35)',
          fillerColor: 'rgba(139, 92, 246, 0.18)',
          handleStyle: { color: '#a855f7' },
          textStyle: { color: '#9ca3af', fontSize: 10 },
        },
      ],
    };
  }, [trace]);

  if (!trace && !loading) {
    return (
      <section className="card">
        <header className="mb-2">
          <h2 className="section-title !mb-0">Tympanic-membrane displacement</h2>
          <p className="text-xs text-gray-500">
            Run a simulation to populate the TM volume-displacement trace.
          </p>
        </header>
        <div className="h-72 grid place-items-center text-gray-600 text-sm italic">
          Waiting for simulation data.
        </div>
      </section>
    );
  }

  return (
    <section className="card">
      {option && (
        <ReactECharts
          option={option}
          style={{ height: `${height}px`, width: '100%' }}
          opts={{ renderer: 'canvas' }}
          notMerge
        />
      )}
    </section>
  );
}

export default TmDisplacementChart;
