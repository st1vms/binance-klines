import sqlite3
from config import SQLITE_EUR_PAIRS_DB_FILEPATH
from dataclasses import dataclass, field


@dataclass(order=True)
class KLinesData:
    sort_index: int = field(init=False, repr=False)

    open_time: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    close_time: int
    quote_asset_volume: float
    n_trades: int
    taker_buy_base_volume: float
    taker_buy_quote_volume: float

    def __post_init__(self):
        self.sort_index = self.open_time


@dataclass(frozen=True)
class CryptoPairData:
    symbol: str
    klines: list[KLinesData]


async def ensure_db_exists(symbols: list[str]):
    con = sqlite3.connect(SQLITE_EUR_PAIRS_DB_FILEPATH)
    try:
        with con:
            c = con.cursor()
            for symbol in symbols:
                c.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (symbol,),
                )
                table_exists = c.fetchone()

                if not table_exists:
                    # Create the table only if it doesn't exist for the symbol
                    c.execute(
                        f"CREATE TABLE {symbol} ("
                        "open_time INTEGER PRIMARY KEY,"
                        "open_price REAL,"
                        "high_price REAL,"
                        "low_price REAL,"
                        "close_price REAL,"
                        "volume REAL,"
                        "close_time INTEGER,"
                        "quote_asset_volume REAL,"
                        "n_trades INTEGER,"
                        "taker_buy_base_volume REAL,"
                        "taker_buy_quote_volume REAL"
                        ")"
                    )
    finally:
        con.close()


async def update_db(symbol: str, klines: list[KLinesData]):
    con = sqlite3.connect(SQLITE_EUR_PAIRS_DB_FILEPATH)
    try:
        with con:
            c = con.cursor()
            for kline in klines:
                # Check if the KLine with the same open_time already exists in the table
                existing_data = c.execute(
                    f"SELECT * FROM {symbol} WHERE open_time = ?", (kline.open_time,)
                ).fetchone()

                if existing_data:
                    # KLine with the same open_time exists, skip it
                    continue

                # Insert the new KLine as a new row
                c.execute(
                    f"INSERT INTO {symbol} VALUES " "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        kline.open_time,
                        kline.open_price,
                        kline.high_price,
                        kline.low_price,
                        kline.close_price,
                        kline.volume,
                        kline.close_time,
                        kline.quote_asset_volume,
                        kline.n_trades,
                        kline.taker_buy_base_volume,
                        kline.taker_buy_quote_volume,
                    ),
                )
    finally:
        con.close()


async def get_table_names():
    con = sqlite3.connect(SQLITE_EUR_PAIRS_DB_FILEPATH)
    try:
        with con:
            c = con.cursor()

            # Query the database schema to get the names of all tables
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = c.fetchall()

            # Extract the table names (crypto symbols) and
            table_names_list = [table_name[0] for table_name in table_names]

            return table_names_list
    finally:
        con.close()


async def get_latest_kline(symbol: str) -> KLinesData:
    con = sqlite3.connect(SQLITE_EUR_PAIRS_DB_FILEPATH)
    try:
        with con:
            c = con.cursor()
            # Get the latest KLine for the specified symbol based on open_time (timestamp)
            c.execute(f"SELECT * FROM {symbol} ORDER BY open_time DESC LIMIT 1")
            latest_kline = c.fetchone()

            if latest_kline:
                # If the latest KLine exists, create a KLinesData instance with the data and return it
                kline_data = KLinesData(*latest_kline)
                return kline_data
            else:
                # If no KLines exist for the specified symbol, return None
                return None
    finally:
        con.close()


async def get_all_klines_from_symbol_table(symbol: str) -> list[KLinesData]:
    con = sqlite3.connect(SQLITE_EUR_PAIRS_DB_FILEPATH)
    try:
        with con:
            c = con.cursor()

            # Get all KLines for the specified symbol from the table, sorted by open_time in ascending order
            c.execute(f"SELECT * FROM {symbol} ORDER BY open_time ASC")
            all_klines = c.fetchall()

            # Convert the list of fetched data into a list of KLinesData instances
            klines_data_list = [KLinesData(*kline) for kline in all_klines]

            return klines_data_list
    finally:
        con.close()
