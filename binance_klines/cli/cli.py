"""cli module"""

import asyncio
from dataclasses import dataclass
from binance_klines import BinanceKlineFetcher, KlineDatabase, CryptoPairData
from binance_klines.utils.config import ConfigObject, format_config
from binance_klines.utils.logger import log

# Exit variables
EXIT_SUCCESS = 0
EXIT_FAILURE = -1


@dataclass
class BinanceAuth(ConfigObject):
    """Binance authentication config"""

    section: str = "AUTH"

    API_KEY: str = None
    API_SECRET: str = None


async def _main() -> int:

    log.info("Starting...")
    auth = BinanceAuth()

    if auth.API_KEY is None or auth.API_SECRET is None:
        raise ValueError("Binance Auth credentials not set!")

    database = KlineDatabase()
    log.info("Database created at: %s", database.config.FILE_PATH)

    fetcher = BinanceKlineFetcher(auth.API_KEY, auth.API_SECRET)

    log.info("Fetcher configuration: %s", format_config(fetcher.config_params))

    pair: CryptoPairData = await fetcher.fetch_pair()
    if pair is None:
        log.error("Unable to fetch klines for this crypto pair!")
        return EXIT_FAILURE

    for kline in pair.klines:
        database.add_kline(kline)

    log.info("Successfully saved %d klines into database!", len(pair.klines))

    return EXIT_SUCCESS


def main() -> int:
    """main entry point"""
    return asyncio.run(_main())
