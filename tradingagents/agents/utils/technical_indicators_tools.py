from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor

@tool
def get_indicators(
    symbol: Annotated[str, "ticker symbol of the instrument (stock, forex, commodity, etc.)"],
    indicator: Annotated[str, "technical indicator(s) to get the analysis and report of. Can be a single indicator or comma-separated list of indicators (e.g., 'rsi,macd,boll')"],
    curr_date: Annotated[str, "The current trading date you are trading on, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"] = 30,
    interval: Annotated[str, "Data interval. Valid options: 1d, 90m, 1h, 30m, 15m, 5m"] = "1d",
) -> str:
    """
    Retrieve technical indicators for a given ticker symbol.
    Uses the configured technical_indicators vendor.
    Args:
        symbol (str): Ticker symbol of the instrument, e.g. AAPL, XAUUSD, GC=F
        indicator (str): Technical indicator(s) to analyze. Can be single or comma-separated list.
                        Single: 'rsi'
                        Multiple: 'rsi,macd,boll'
        curr_date (str): The current trading date you are trading on, YYYY-mm-dd
        look_back_days (int): How many days to look back, default is 30
        interval (str): Data interval (1d, 90m, 1h, 30m, 15m, 5m), default is 1d
    Returns:
        str: A formatted report containing the technical indicators for the specified ticker symbol.
    """
    return route_to_vendor("get_indicators", symbol, indicator, curr_date, look_back_days, interval=interval)