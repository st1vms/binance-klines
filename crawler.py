import asyncio
import traceback
import datetime
from time import time
from binance.client import AsyncClient, BinanceAPIException, HistoricalKlinesType
from datab import *
from utils import *
from config import (
    WEIGHT_RATELIMIT_ERROR_CODE,
    WEIGHT_RATELIMIT_TIMEOUT_SECONDS,
    DEFAULT_KLINES_TYPE,
)


async def __get_historical_klines(
    client: AsyncClient,
    symbol: str,
    time_window: str,
    start_time_millis: int = None,
    end_time_millis: int = None,
    klines_type: HistoricalKlinesType = DEFAULT_KLINES_TYPE,
) -> list[KLinesData]:
    # Receives klines data

    while True:
        try:
            symbol = denormalize_symbol_name(symbol)
            res = await client.get_historical_klines(
                symbol=symbol,
                interval=time_window,
                start_str=start_time_millis,
                end_str=end_time_millis,
                klines_type=klines_type,
            )
            # Update klines data into dataclass, removing last unused field '0' (see docs)
            klines = [KLinesData(*k[:-1]) for k in res]
            return klines
        except BinanceAPIException as e:
            if str(e).find(str(WEIGHT_RATELIMIT_ERROR_CODE)) != -1:
                print(
                    f"Weight ratelimit was hit! Waiting {WEIGHT_RATELIMIT_TIMEOUT_SECONDS} seconds...",
                    end="\r",
                )
                await asyncio.sleep(WEIGHT_RATELIMIT_TIMEOUT_SECONDS)
                continue
            print(f"\nGot unexpected BinaceAPIException {str(e)}")
        except Exception:
            print("\nUnexpected Exception")
            traceback.print_exc()
            return []


async def get_pairs_data_async(
    client: AsyncClient,
    symbols: list[str],
    time_window: str,
    start_time_millis: int = None,
    end_time_millis: int = None,
) -> dict[str, CryptoPairData]:
    if start_time_millis and end_time_millis:
        if start_time_millis >= end_time_millis:
            raise ValueError(
                f"\nInvalid time parameters: {start_time_millis} >= {end_time_millis}"
            )

    _sTime = datetime.datetime.fromtimestamp(
        start_time_millis / 1000 if start_time_millis else 0
    )
    _eTime = datetime.datetime.fromtimestamp(
        end_time_millis / 1000 if end_time_millis else time()
    )
    print(f"\nCrawling historical crypto pairs data from {_sTime} to {_eTime}")

    _res_symbols = {}

    # Crawler task
    async def _task(client, symbol):
        # Crawl different data in parallel

        latest_kline = await get_latest_kline(
            symbol,
        )

        if latest_kline and latest_kline.close_time > time() * 1000:
            # Skip if latest kline is updated
            return

        s = latest_kline.open_time if latest_kline else start_time_millis

        (klines,) = await asyncio.gather(
            __get_historical_klines(
                client,
                symbol,
                time_window,
                s,
                end_time_millis,
            )
        )

        # Save CryptoPairData entry in dictionary
        _res_symbols[symbol] = CryptoPairData(
            symbol=symbol,
            klines=klines,
        )

    tasks = []
    for symbol in symbols:
        # Append task if symbol is not present or if it matches
        tasks.append(asyncio.create_task(_task(client, symbol)))

    # Run crawlers for every symbol in parallel
    await asyncio.gather(*tasks)

    print("\nAll historical data crawled")
    return _res_symbols


async def get_pairs_data_sync(
    client: AsyncClient,
    symbols: list[str],
    time_window: str,
    start_time_millis: int = None,
    end_time_millis: int = None,
) -> dict[str, CryptoPairData]:
    if start_time_millis and end_time_millis:
        if start_time_millis >= end_time_millis:
            raise ValueError(
                f"\nInvalid time parameters: {start_time_millis} >= {end_time_millis}"
            )

    _sTime = datetime.datetime.fromtimestamp(
        start_time_millis / 1000 if start_time_millis else 0
    )
    _eTime = datetime.datetime.fromtimestamp(
        end_time_millis / 1000 if end_time_millis else time()
    )
    print(f"\nCrawling historical crypto pairs data from {_sTime} to {_eTime}")

    __res_symbols = {}

    for symbol in symbols:
        latest_kline = await get_latest_kline(symbol)

        if latest_kline and latest_kline.close_time > time() * 1000:
            # Skip if latest kline is updated
            return

        s = latest_kline.open_time if latest_kline else start_time_millis

        (klines,) = await asyncio.gather(
            __get_historical_klines(
                client,
                symbol,
                time_window,
                s,
                end_time_millis,
            )
        )

        # Save CryptoPairData entry in dictionary
        __res_symbols[symbol] = CryptoPairData(
            symbol=symbol,
            klines=klines,
        )

    print("\nAll historical data crawled")
    return __res_symbols
