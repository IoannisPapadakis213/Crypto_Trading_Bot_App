"use client";

import { useSyncExternalStore } from "react";
import { MockMarketEngine } from "./mock-market-engine";
import type { MarketSnapshot } from "./types";

const TICK_MS = 1000;

// A module-level singleton, not per-component state: the engine seeds itself
// with Math.random()/Date.now(), so it must only ever be read on the client.
// useSyncExternalStore's getServerSnapshot (always null) keeps the server and
// first client render identical, avoiding a hydration mismatch.
let engine: MockMarketEngine | null = null;
function getEngine(): MockMarketEngine {
  if (!engine) engine = new MockMarketEngine();
  return engine;
}

function subscribe(onStoreChange: () => void): () => void {
  const interval = setInterval(() => {
    getEngine().tick();
    onStoreChange();
  }, TICK_MS);
  return () => clearInterval(interval);
}

function getSnapshot(): MarketSnapshot {
  return getEngine().snapshot();
}

function getServerSnapshot(): MarketSnapshot | null {
  return null;
}

export function useMockMarket(): MarketSnapshot | null {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
