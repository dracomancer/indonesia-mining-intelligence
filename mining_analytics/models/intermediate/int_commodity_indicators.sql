
with commodity_data as (

    select *
    from {{ ref('stg_commodity_prices') }}

),

indicators as (

    select
        *,

        -- 20-day moving average
        avg(close_price) over (
            partition by symbol
            order by price_timestamp
            rows between 19 preceding and current row
        ) as calculated_sma_20,

        -- 50-day moving average
        avg(close_price) over (
            partition by symbol
            order by price_timestamp
            rows between 49 preceding and current row
        ) as calculated_sma_50,

        -- 20-day historical volatility
        stddev_samp(daily_return_pct) over (
            partition by symbol
            order by price_timestamp
            rows between 19 preceding and current row
        ) as calculated_volatility_20d,

        -- 20-day high and low
        max(high_price) over (
            partition by symbol
            order by price_timestamp
            rows between 19 preceding and current row
        ) as high_20d,

        min(low_price) over (
            partition by symbol
            order by price_timestamp
            rows between 19 preceding and current row
        ) as low_20d

    from commodity_data

)

select *
from indicators
