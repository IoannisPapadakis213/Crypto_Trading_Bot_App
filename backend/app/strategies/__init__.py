"""Strategy package. Importing this module registers all built-in strategies."""

from app.strategies.bollinger_bands import BollingerBandsStrategy
from app.strategies.ma_crossover import MovingAverageCrossoverStrategy
from app.strategies.rsi_mean_reversion import RsiMeanReversionStrategy

__all__ = [
    "BollingerBandsStrategy",
    "MovingAverageCrossoverStrategy",
    "RsiMeanReversionStrategy",
]
