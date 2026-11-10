
with source_data as (

    select *
    from {{ ref('stg_world_bank_commodity_prices') }}

),

calculated_returns as (

    select
        trading_date,
        symbol,
        commodity_name,
        close_price,
        unit,
        data_source,
        frequency,
        ingested_at,

        (
            close_price / nullif(
                lag(close_price) over (
                    partition by symbol
                    order by trading_date
                ),
                0
            ) - 1
        ) * 100 as monthly_return_pct

    from source_data

),

calculated_indicators as (

    select
        *,

        avg(close_price) over (
            partition by symbol
            order by trading_date
            rows between 2 preceding and current row
        ) as sma_3m,

        avg(close_price) over (
            partition by symbol
            order by trading_date
            rows between 5 preceding and current row
        ) as sma_6m,

        -- Standard deviation of monthly returns
        stddev_samp(monthly_return_pct) over (
            partition by symbol
            order by trading_date
            rows between 2 preceding and current row
        ) as volatility_3m,

        max(close_price) over (
            partition by symbol
            order by trading_date
            rows between 11 preceding and current row
        ) as high_12m,

        min(close_price) over (
            partition by symbol
            order by trading_date
            rows between 11 preceding and current row
        ) as low_12m

    from calculated_returns

)

select *
from calculated_indicators
