"""Binance Kline fetcher module"""

from dataclasses import dataclass
from binance_klines.database import KlineData, CryptoPairData, KlineDatabase
from binance_klines.utils.config import ConfigObject


@dataclass(frozen=True)
class KlineRequestParams(ConfigObject):
    """Kline Request parameters"""

    section: str = "REQUEST_PARAMS"

    PAIR_SYMBOL: str

    CONTRACT_TYPE: int

    INTERVAL: int

    START_TIME: int
    END_TIME: int

    LIMIT: int = 500


class BinanceKlineFetcher:
    """Binance Kline fetcher object"""

    def __init__(self) -> None:
        pass
