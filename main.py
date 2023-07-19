import os
import asyncio
import datetime
from binance.client import AsyncClient
from datab import *
from crawler import *
from stats import *
from utils import *
from config import *

CREDENTIALS_FILENAME = "creds"


def ask_credentials() -> tuple[str, str] | None:
    if os.path.exists(CREDENTIALS_FILENAME):
        with open(CREDENTIALS_FILENAME, "r") as fp:
            lines = fp.readlines()
            return lines[0].rstrip(), lines[1].rstrip()

    key = input("\nInsert Binance API key\n>>").lstrip().rstrip()
    secret = input("\nInsert Binance API secret\n>>").lstrip().rstrip()
    if not key or not secret:
        return None

    with open(CREDENTIALS_FILENAME, "w") as fp:
        fp.write(f"{key}\n{secret}")

    return key, secret


async def main(api_key: str, api_secret: str):
    client = await AsyncClient.create(api_key=api_key, api_secret=api_secret)
    try:
        pair = input("\nInsert crypto pair\n>>").lstrip().rstrip()
        time_off = int(input("\nInsert time offset minutes\n>>").lstrip().rstrip())

        # Retrieve symbols informations
        symbols = [s for s in await get_table_names() if not pair or s.find(pair) != -1]

        await ensure_db_exists(symbols)

        eur_pairs = await get_pairs_data_async(client, symbols, DEFAULT_TIME_WINDOW)

        for k in eur_pairs.keys():
            k = normalize_symbol_name(k)
            await update_db(k, eur_pairs[k].klines)

        stats = []
        for symbol in symbols:
            if symbol.find(pair) != -1:
                data = await get_all_klines_from_symbol_table(symbol)
                if data:
                    (
                        buy_signal,
                        estimated_price,
                        estimated_timestamp,
                        percentage_difference,
                    ) = analyze_crypto_pair(data, time_off)

                    stats.append(
                        (
                            symbol,
                            buy_signal,
                            estimated_price,
                            estimated_timestamp,
                            percentage_difference,
                            data[-1].close_price,
                        )
                    )

        stats = sorted(stats, key=lambda x: x[4])

        for s in stats:
            print(f"\n\nStats for {s[0]}")
            print(f"\n\nSignal: {s[1]}")
            print("Latest close price:", s[5])
            print("Estimated price:", s[2])
            print(
                "Estimated timestamp:",
                datetime.datetime.fromtimestamp(s[3] / 1000),
            )
            print("Percentage difference:", s[4], "%")
            stop, limit = calculate_stop_limit_prices(s[5], s[2], RISK_MARGIN, s[1])
            if stop and limit:
                print(f"\nStop at:{stop} limit at:{limit})")
    finally:
        await client.close_connection()


if __name__ == "__main__":
    key, secret = ask_credentials()
    asyncio.run(main(key, secret))
