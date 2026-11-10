
with latest_stock_data as (

    select
        *,
        row_number() over (
            partition by symbol
            order by trading_date desc
        ) as row_num

    from {{ ref('int_stock_indicators') }}

),

stock_performance as (

    select
        trading_date,
        symbol,

        close_price,
        daily_return_pct,

        sma_7,
        sma_20,
        sma_50,

        volatility_20d,
        high_20d,
        low_20d,

        volume,
        turnover_idr,

        case
            when close_price > sma_20
                and sma_20 > sma_50
                then 'Bullish'

            when close_price < sma_20
                and sma_20 < sma_50
                then 'Bearish'

            else 'Neutral'
        end as trend_signal

    from latest_stock_data
    where row_num = 1

)

select
    *,
    rank() over (
        order by daily_return_pct desc
    ) as daily_return_rank

from stock_performance
