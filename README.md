# binance-klines

## Installation

Run this command inside the repository folder:

```shell
pip install -e .
```

## How to use

Inside a newly created folder, open a terminal and run:

```shell
binance-klines
```

A newly created database holding the kline data will be generated inside this folder.

## Example configuration

Create a file named `config.ini` inside current directory
This file can have the following options:

```ini
[AUTH]
API_KEY=test
API_SECRET=test

[DATABASE]
FILE_PATH=test.db

[REQUEST_PARAMS]
PAIR_SYMBOL=BTCEUR

CONTRACT_TYPE="PERPETUAL"

INTERVAL=1h

START_TIME = 1706194141
END_TIME = 0

LIMIT=500
```
