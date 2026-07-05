"""Seam for a future ML-based strategy.

Not implemented yet — no model is trained or shipped in this phase. This
exists so that adding a real ML strategy later means implementing
`FeaturePipeline` and `MLStrategy.predict`, without touching the runner,
broker, or risk manager (they only ever depend on the `Strategy` interface).
"""

from abc import ABC, abstractmethod

import pandas as pd

from app.strategies.base import Signal, Strategy


class FeaturePipeline(ABC):
    """Transforms raw candles into a model-ready feature frame."""

    @abstractmethod
    def transform(self, candles: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class MLStrategy(Strategy):
    """Base class for model-backed strategies.

    Concrete subclasses supply a `FeaturePipeline` and a `predict` method;
    `on_candle` wires them together so the rest of the system keeps treating
    this like any other `Strategy`.
    """

    def __init__(self, feature_pipeline: FeaturePipeline) -> None:
        self.feature_pipeline = feature_pipeline

    @abstractmethod
    def predict(self, features: pd.DataFrame) -> Signal:
        raise NotImplementedError

    def on_candle(self, candles: pd.DataFrame) -> Signal:
        features = self.feature_pipeline.transform(candles)
        return self.predict(features)
