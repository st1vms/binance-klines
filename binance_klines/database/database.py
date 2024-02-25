"""Database module"""

from sqlite3 import connect as db_connect
from typing import Iterator, Callable, Any
from dataclasses import dataclass
from binance_klines.utils.config import ConfigObject
from .klines import KlineData


@dataclass(frozen=True)
class KlineDatabaseConfig(ConfigObject):
    """Kline Database config object"""

    section: str = "DATABASE"

    FILE_PATH: str = "klines.db"


CONFIG = KlineDatabaseConfig()


class KlineDatabase:
    """Kline Database object"""

    def __init__(self) -> None:
        self.connection = None
        self.create_table()

    def __enter__(self):
        """Enter the context"""
        self.connect()
        return self

    def __exit__(self, *args, **kwargs):
        """Exit the context"""
        self.disconnect()

    def connect(self):
        """Connect to database"""
        self.connection = db_connect(CONFIG.FILE_PATH)

    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()

    def create_table(self):
        """Create database table"""
        self.connect()
        try:
            query = """
            CREATE TABLE IF NOT EXISTS kline_data (
                open_time INTEGER PRIMARY KEY,
                close_time INTEGER,
                open_price REAL,
                highest_price REAL,
                lowest_price REAL,
                close_price REAL,
                volume REAL,
                base_asset_volume REAL,
                number_of_trades INTEGER,
                taker_buy_base_asset_volume REAL,
                taker_buy_quote_asset_volume REAL
            );
            CREATE INDEX IF NOT EXISTS idx_close_time ON kline_data (close_time);
            """
            self.connection.execute(query)
            self.connection.commit()
        finally:
            self.disconnect()

    def add_kline(self, kline: KlineData) -> None:
        """Add KlineData to database"""
        self.connect()
        try:
            query = """
            INSERT INTO kline_data (
                open_time,
                close_time,
                open_price,
                highest_price,
                lowest_price,
                open_price,
                volume,
                base_asset_volume,
                number_of_trades,
                taker_buy_base_asset_volume,
                taker_buy_quote_asset_volume
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                kline.open_time,
                kline.close_time,
                kline.open_price,
                kline.highest_price,
                kline.lowest_price,
                kline.close_price,
                kline.volume,
                kline.base_asset_volume,
                kline.number_of_trades,
                kline.taker_buy_base_asset_volume,
                kline.taker_buy_quote_asset_volume,
            )
            self.connection.execute(query, values)
            self.connection.commit()
        finally:
            self.disconnect()

    def iterate_klines(
        self, filter_func: Callable[[KlineData, Any]] = None
    ) -> Iterator[KlineData]:
        """Iterate over klines"""
        self.connect()
        try:
            query = "SELECT * FROM kline_data ORDER BY open_time ASC"
            cursor = self.connection.execute(query)

            row = cursor.fetchone()
            if row is None:
                return  # No entries in the database

            while row is not None:
                kline = KlineData(
                    open_time=row[0],
                    close_time=row[1],
                    open_price=row[2],
                    highest_price=row[3],
                    lowest_price=row[4],
                    close_price=row[5],
                    volume=row[6],
                    base_asset_volume=row[7],
                    trades_count=row[8],
                    taker_buy_base_asset_volume=row[9],
                    taker_buy_quote_asset_volume=row[10],
                )
                if filter_func is not None and not filter_func(kline):
                    row = cursor.fetchone()
                    continue
                yield kline
                row = cursor.fetchone()
        finally:
            self.disconnect()
