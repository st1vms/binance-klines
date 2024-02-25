"""Binance Kline fetcher module"""

from time import time
from dataclasses import dataclass
from binance.client import AsyncClient, HistoricalKlinesType
from binance_klines.database import CryptoPairData, KlineData
from binance_klines.utils.config import ConfigObject
from binance_klines.utils.logger import log


@dataclass
class KlineRequestParams(ConfigObject):
    """Kline Request parameters"""

    section: str = "REQUEST_PARAMS"

    PAIR_SYMBOL: str = None

    CONTRACT_TYPE: str = None

    INTERVAL: str = "1h"

    START_TIME: int = 946684800  # year 2000
    END_TIME: int = 0

    LIMIT: int = 500


class BinanceKlineFetcher:
    """Binance Kline fetcher object"""

    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.config_params = KlineRequestParams()
        self.client: AsyncClient = None

    async def fetch_pair(self) -> CryptoPairData | None:
        """Fetch data for configured crypto pair"""

        self.client = await AsyncClient.create(
            api_key=self.api_key, api_secret=self.api_secret
        )
        try:
            log.info("Fetching klines for symbol: %s", self.config_params.PAIR_SYMBOL)
            return await self.get_historical_spot_klines()
        finally:
            await self.client.close_connection()

    async def get_historical_klines(
        self, kline_type: HistoricalKlinesType
    ) -> list[KlineData]:
        """Retrieves klines data"""

        if self.config_params.START_TIME and self.config_params.END_TIME:
            if self.config_params.START_TIME >= self.config_params.END_TIME:
                raise ValueError(
                    "\nInvalid time parameters:"
                    f"{self.config_params.START_TIME} >= {self.config_params.END_TIME}"
                )
        start_time = (
            int(self.config_params.START_TIME if self.config_params.START_TIME else 0)
            * 1000
        )
        end_time = (
            int(self.config_params.END_TIME if self.config_params.END_TIME else time())
            * 1000
        )

        log.info(
            "Getting Historical Spot Klines:\n"
            "Interval: %s\nStart time: %s\nEnd time: %s",
            self.config_params.INTERVAL,
            start_time,
            end_time,
        )

        res = await self.client.get_historical_klines(
            symbol=self.config_params.PAIR_SYMBOL,
            interval=self.config_params.INTERVAL,
            start_str=start_time,
            end_str=end_time,
            limit=self.config_params.LIMIT,
            klines_type=kline_type,
        )
        klines = []
        for kline in res:
            kline = kline[:-1]
            klines.append(KlineData(*kline))
        return CryptoPairData(self.config_params.PAIR_SYMBOL, klines)

    async def get_historical_spot_klines(self) -> list[KlineData]:
        """Retrieves Spot klines data"""
        return await self.get_historical_klines(HistoricalKlinesType.SPOT)
