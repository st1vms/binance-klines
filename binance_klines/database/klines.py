"""Kline object definition module"""

from dataclasses import dataclass


@dataclass(order=True)
class KlineData:
    """Kline dataclass"""

    open_time: int
    close_time: int

    open_price: float
    close_price: float

    highest_price: float
    lowest_price: float

    volume: float
    base_asset_volume: float

    trades_count: int

    taker_buy_quote_asset_volume: float
    taker_buy_base_asset_volume: float


@dataclass(frozen=True)
class CryptoPairData:
    """Crypto Pair dataclass"""

    symbol: str
    klines: list[KlineData]
