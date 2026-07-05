"use client";

import { useEffect, useRef } from "react";
import {
  AreaSeries,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
  createChart,
} from "lightweight-charts";
import type { EquityPoint } from "@/lib/types";

export function EquityCurve({
  equityCurve,
  startingCash,
}: {
  equityCurve: EquityPoint[];
  startingCash: number;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<ISeriesApi<"Area"> | null>(null);
  const chartRef = useRef<IChartApi | null>(null);

  const isUp = (equityCurve.at(-1)?.equity ?? startingCash) >= startingCash;
  const lineColor = isUp ? "#0ca30c" : "#d03b3b";
  const topColor = isUp ? "rgba(12,163,12,0.28)" : "rgba(208,59,59,0.28)";

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      layout: { background: { color: "transparent" }, textColor: "#c3c2b7" },
      grid: { vertLines: { visible: false }, horzLines: { color: "#2c2c2a" } },
      rightPriceScale: { borderColor: "#383835" },
      timeScale: { borderColor: "#383835", timeVisible: true },
      autoSize: true,
      handleScroll: false,
      handleScale: false,
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor,
      topColor,
      bottomColor: "rgba(0,0,0,0)",
      lineWidth: 2,
      priceFormat: { type: "price", precision: 0, minMove: 1 },
    });

    chartRef.current = chart;
    seriesRef.current = series;
    return () => {
      chart.remove();
      chartRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    seriesRef.current?.applyOptions({ lineColor, topColor });
  }, [lineColor, topColor]);

  useEffect(() => {
    if (!seriesRef.current || equityCurve.length === 0) return;
    seriesRef.current.setData(
      equityCurve.map((p) => ({ time: p.time as UTCTimestamp, value: p.equity })),
    );
  }, [equityCurve]);

  return <div ref={containerRef} className="h-full min-h-0 w-full" />;
}
