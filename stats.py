from datab import KLinesData
import datetime


def moving_average_crossover(
    price_data: list[float], short_window: int, long_window: int
):
    short_ma = sum(price_data[-short_window:]) / short_window
    long_ma = sum(price_data[-long_window:]) / long_window

    short_slope = (price_data[-1] - price_data[-short_window]) / short_window

    if short_ma > long_ma and short_slope > 0:
        return "BUY"
    elif short_ma < long_ma and short_slope < 0:
        return "SELL"
    else:
        return "HOLD"


def estimate_windows_based_on_time_interval(interval_minutes: int) -> tuple:
    # Define your calibration logic here based on the interval_minutes
    # You can adjust the short and long windows based on the interval

    # Example calibration logic:
    if interval_minutes <= 15:
        short_window = 5
        long_window = 20
    elif interval_minutes <= 60:
        short_window = 10
        long_window = 50
    elif interval_minutes <= 240:
        short_window = 20
        long_window = 100
    else:
        short_window = 30
        long_window = 150

    return short_window, long_window


def analyze_crypto_pair(klines_data: list[KLinesData], prediction_minutes: int):
    price_data = [float(kline.close_price) for kline in klines_data]

    # Calculate the time difference between the last two timestamps
    last_timestamp = klines_data[-1].close_time
    second_last_timestamp = klines_data[-2].close_time
    time_difference_minutes = abs(
        (last_timestamp - second_last_timestamp) // (60 * 1000)
    )

    # Calibrate the short and long windows based on the time interval
    short_window, long_window = estimate_windows_based_on_time_interval(
        time_difference_minutes
    )

    if len(price_data) < long_window:
        return (0, 0, 0, 0)

    signal = moving_average_crossover(price_data, short_window, long_window)

    # Perform analysis with the calibrated windows
    short_window_data = price_data[-short_window:]
    long_window_data = price_data[-long_window:]

    # Get the current timestamp
    current_timestamp = (
        datetime.datetime.now().timestamp() * 1000
    )  # Convert to milliseconds

    # Calculate the future timestamp based on prediction_minutes
    prediction_timestamp = current_timestamp + (prediction_minutes * 60 * 1000)

    # Predict the price at the specified future timestamp
    last_price = price_data[-1]
    price_change_ratio = sum(
        short / long for short, long in zip(short_window_data, long_window_data)
    ) / len(short_window_data)
    estimated_price = last_price * price_change_ratio

    # Estimate the percentage difference between the estimated price and the last price
    percentage_difference = ((estimated_price - last_price) / last_price) * 100

    return signal, estimated_price, prediction_timestamp, percentage_difference


def calculate_stop_limit_prices(
    latest_close_price: float, estimated_price: float, risk_margin: float, signal: str
):
    if signal == "BUY":
        # Calculate the stop price based on the latest close price and the desired risk margin
        stop_price = latest_close_price * (1 - (risk_margin / 100))

        # Calculate the limit price based on the estimated price and the desired risk margin
        limit_price = estimated_price * (1 + (risk_margin / 100))
    elif signal == "SELL":
        # Calculate the stop price based on the latest close price and the desired risk margin
        stop_price = latest_close_price * (1 + (risk_margin / 100))

        # Calculate the limit price based on the estimated price and the desired risk margin
        limit_price = estimated_price * (1 - (risk_margin / 100))
    else:
        # For HOLD signals, set stop and limit prices to None
        stop_price = None
        limit_price = None

    return stop_price, limit_price
