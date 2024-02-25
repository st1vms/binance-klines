"""Binance Kline fetcher module"""

from dataclasses import dataclass
from binance_klines.database import CryptoPairData
from binance_klines.utils.config import ConfigObject
from binance_klines.utils.logger import log


@dataclass
class KlineRequestParams(ConfigObject):
    """Kline Request parameters"""

    section: str = "REQUEST_PARAMS"

    PAIR_SYMBOL: str = None

    CONTRACT_TYPE: str = None

    INTERVAL: str = "1h"

    START_TIME: int = 0
    END_TIME: int = 0

    LIMIT: int = 500


class BinanceKlineFetcher:
    """Binance Kline fetcher object"""

    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.config_params = KlineRequestParams()

    def fetch_pair(self) -> CryptoPairData | None:
        """Fetch data for configured crypto pair"""

        log.info("Fetching klines for symbol: %s", self.config_params.PAIR_SYMBOL)

        return None
