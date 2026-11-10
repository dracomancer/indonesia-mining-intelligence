
select
    trading_date,
    symbol,

    open_price,
    high_price,
    low_price,
    close_price,
    adjusted_close,
    volume,

    daily_return_pct,
    sma_7,
    sma_20,
    sma_50,

    volatility_20d,
    high_20d,
    low_20d,

    turnover_idr,
    intraday_range_pct

from {{ ref('int_stock_indicators') }}
