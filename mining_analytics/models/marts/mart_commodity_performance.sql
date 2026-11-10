
with commodity_data as (

    select *
    from {{ ref('int_commodity_indicators') }}

),

latest_prices as (

    select
        *,
        row_number() over (
            partition by symbol
            order by price_timestamp desc
        ) as row_num

    from commodity_data

),

performance as (

    select
        price_timestamp,
        trading_date,
        symbol,
        commodity_name,
        category,
        unit,

        close_price,
        daily_return_pct,
        price_change,

        calculated_sma_20 as sma_20,
        calculated_sma_50 as sma_50,

        calculated_volatility_20d as volatility_20d,

        high_20d,
        low_20d,

        data_source,
        market,

        case
            when close_price > calculated_sma_20
             and calculated_sma_20 > calculated_sma_50
                then 'Bullish'

            when close_price < calculated_sma_20
             and calculated_sma_20 < calculated_sma_50
                then 'Bearish'

            else 'Neutral'
        end as trend_signal

    from latest_prices
    where row_num = 1

)

select
    *,
    rank() over (
        order by daily_return_pct desc
    ) as daily_return_rank

from performance
