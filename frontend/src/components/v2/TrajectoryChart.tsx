/**
 * TrajectoryChart — signature time-domain plot of the v2 physics run.
 *
 * Shows, for a single simulated exposure:
 *  - Altitude (ft, left Y axis) as a filled area line.
 *  - ΔP = P_ME − P_ambient (mmHg, right Y axis) as a line.
 *  - The three clinical ΔP thresholds (barotitis 18.4, baromyringitis
 *    95.6, rupture 150) as reference lines on the ΔP axis.
 *  - Per-sample ET-open state as a thin green band at the top of the
 *    chart area (markArea, rendered only while ``et_open`` is true).
 *  - Swallow events as small tick scatter below the chart.
 *  - Valsalva events as larger red scatter on the same strip.
 *
 * No physics here — all arrays come from ``trace`` on the simulate
 * response. Rendering only.
 */

import ReactECharts from 'echarts-for-react';
import { useMemo } from 'react';

import { baseChartOption, colorSchemes } from '../../lib/chartTheme';
import type { SimulationTraceV2 } from '../../types/v2';

interface TrajectoryChartProps {
  trace: SimulationTraceV2 | null;
  height?: number;
  loading?: boolean;
}

function compressEtOpenRuns(
  t_s: number[],
  et_open: boolean[],
): Array<[number, number]> {
  const runs: Array<[number, number]> = [];
  let start: number | null = null;
  for (let i = 0; i < et_open.length; i++) {
    if (et_open[i] && start === null) start = t_s[i];
    if (!et_open[i] && start !== null) {
      runs.push([start / 60, t_s[i] / 60]);
      start = null;
    }
  }
  if (start !== null) runs.push([start / 60, t_s[t_s.length - 1] / 60]);
  return runs;
}

export function TrajectoryChart({
  trace,
  height = 480,
  loading = false,
}: TrajectoryChartProps) {
  const option = useMemo(() => {
    if (!trace) return null;

    const tMinutes = trace.t_s.map((t) => t / 60);
    const altitudeSeries = trace.altitude_ft.map((a, i) => [tMinutes[i], a]);
    const deltaPSeries = trace.delta_p_mmHg.map((dp, i) => [tMinutes[i], dp]);
    const etOpenRuns = compressEtOpenRuns(trace.t_s, trace.et_open);
    const swallowPoints = trace.swallow_events_s.map((t) => [t / 60, 0]);
    const valsalvaPoints = trace.valsalva_events_s.map((t) => [t / 60, 0]);

    const markAreaData = etOpenRuns.map(([from, to]) => [
      { xAxis: from, itemStyle: { color: 'rgba(34, 197, 94, 0.18)' } },
      { xAxis: to },
    ]);

    return {
      ...baseChartOption,
      title: {
        ...baseChartOption.title,
        text: 'Pressure trajectory',
        subtext:
          'Altitude (left) vs. middle-ear ΔP (right); ET-open intervals shaded green; swallow ticks below, Valsalva pulses in red.',
        top: 8,
        left: 12,
      },
      legend: {
        ...baseChartOption.legend,
        data: ['Altitude', 'ΔP (P_ME − P_ambient)', 'Swallow', 'Valsalva'],
        top: 44,
        right: 16,
      },
      grid: {
        ...baseChartOption.grid,
        top: 96,
        left: 64,
        right: 72,
        bottom: 88,
        containLabel: false,
      },
      tooltip: {
        ...baseChartOption.tooltip,
        trigger: 'axis',
        axisPointer: { type: 'cross', snap: true },
        valueFormatter: (v: number) => (typeof v === 'number' ? v.toFixed(1) : '—'),
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
          name: 'Altitude (ft)',
          position: 'left',
          nameGap: 48,
          nameLocation: 'middle',
          axisLine: { show: true, lineStyle: { color: colorSchemes.anatomy.tympanum } },
        },
        {
          ...baseChartOption.yAxis,
          type: 'value',
          name: 'ΔP (mmHg)',
          position: 'right',
          nameGap: 40,
          nameLocation: 'middle',
          axisLine: { show: true, lineStyle: { color: colorSchemes.pressure.differential } },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: 'Altitude',
          type: 'line',
          yAxisIndex: 0,
          data: altitudeSeries,
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
                { offset: 0, color: 'rgba(139, 92, 246, 0.35)' },
                { offset: 1, color: 'rgba(139, 92, 246, 0.02)' },
              ],
            },
          },
          z: 1,
          markArea: markAreaData.length
            ? {
                silent: true,
                itemStyle: { opacity: 1 },
                data: markAreaData,
              }
            : undefined,
        },
        {
          name: 'ΔP (P_ME − P_ambient)',
          type: 'line',
          yAxisIndex: 1,
          data: deltaPSeries,
          smooth: false,
          symbol: 'none',
          lineStyle: { color: colorSchemes.pressure.differential, width: 2 },
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
                name: 'barotitis 18.4',
                yAxis: 18.4,
                lineStyle: { color: colorSchemes.risk.moderate },
              },
              {
                name: '−18.4',
                yAxis: -18.4,
                lineStyle: { color: colorSchemes.risk.moderate },
              },
              {
                name: 'baromyringitis 95.6',
                yAxis: 95.6,
                lineStyle: { color: '#f97316' },
              },
              {
                name: '−95.6',
                yAxis: -95.6,
                lineStyle: { color: '#f97316' },
              },
              {
                name: 'rupture 150',
                yAxis: 150,
                lineStyle: { color: colorSchemes.risk.high },
              },
              {
                name: '−150',
                yAxis: -150,
                lineStyle: { color: colorSchemes.risk.high },
              },
            ],
          },
        },
        {
          name: 'Swallow',
          type: 'scatter',
          yAxisIndex: 1,
          xAxisIndex: 0,
          data: swallowPoints.map(([x]) => [x, 0]),
          symbol: 'rect',
          symbolSize: [1.5, 8],
          itemStyle: { color: 'rgba(34, 197, 94, 0.75)' },
          tooltip: { show: false },
          z: 3,
        },
        {
          name: 'Valsalva',
          type: 'scatter',
          yAxisIndex: 1,
          xAxisIndex: 0,
          data: valsalvaPoints.map(([x]) => [x, 0]),
          symbol: 'diamond',
          symbolSize: 10,
          itemStyle: { color: colorSchemes.risk.high, borderColor: '#fff', borderWidth: 1 },
          tooltip: {
            show: true,
            formatter: (p: { data: [number, number] }) =>
              `Valsalva @ ${p.data[0].toFixed(2)} min`,
          },
          z: 4,
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
          bottom: 28,
          start: 0,
          end: 100,
          borderColor: 'transparent',
          backgroundColor: 'rgba(17, 24, 39, 0.35)',
          fillerColor: 'rgba(99, 102, 241, 0.18)',
          handleStyle: { color: '#8b5cf6' },
          textStyle: { color: '#9ca3af', fontSize: 10 },
        },
      ],
    };
  }, [trace]);

  if (!trace && !loading) {
    return (
      <section className="card">
        <header className="mb-2">
          <h2 className="section-title !mb-0">Pressure trajectory</h2>
          <p className="text-xs text-gray-500">
            Run a simulation to populate altitude, ΔP, and ET-open state.
          </p>
        </header>
        <div className="h-80 grid place-items-center text-gray-600 text-sm italic">
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

export default TrajectoryChart;
