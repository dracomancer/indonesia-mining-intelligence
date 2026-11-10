
with stock_data as (

    select *
    from {{ ref('stg_stock_prices') }}

),

indicators as (

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
        intraday_range_pct,
        turnover_idr,

        -- Simple moving averages
        avg(close_price) over (
            partition by symbol
            order by trading_date
            rows between 6 preceding and current row
        ) as sma_7,

        avg(close_price) over (
            partition by symbol
            order by trading_date
            rows between 19 preceding and current row
        ) as sma_20,

        avg(close_price) over (
            partition by symbol
            order by trading_date
            rows between 49 preceding and current row
        ) as sma_50,

        -- 20-day historical volatility
        stddev_samp(daily_return_pct) over (
            partition by symbol
            order by trading_date
            rows between 19 preceding and current row
        ) as volatility_20d,

        -- Rolling high and low
        max(high_price) over (
            partition by symbol
            order by trading_date
            rows between 19 preceding and current row
        ) as high_20d,

        min(low_price) over (
            partition by symbol
            order by trading_date
            rows between 19 preceding and current row
        ) as low_20d

    from stock_data

)

select *
from indicators
