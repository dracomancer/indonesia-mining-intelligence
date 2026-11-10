with latest_data as (
    select
        *,
        row_number() over (
            partition by symbol
            order by trading_date desc
        ) as row_num
    from {{ ref('int_world_bank_commodity_indicators') }}
    where close_price is not null
),

performance as (
    select
        trading_date,
        symbol,
        commodity_name,
        close_price,
        unit,
        monthly_return_pct,
        sma_3m,
        sma_6m,
        volatility_3m,
        high_12m,
        low_12m,
        data_source,
        frequency,

        case
            when close_price > sma_3m
                and sma_3m > sma_6m
                then 'Bullish'

            when close_price < sma_3m
                and sma_3m < sma_6m
                then 'Bearish'

            else 'Neutral'
        end as trend_signal

    from latest_data
    where row_num = 1
)

select
    *,
    rank() over (
        order by monthly_return_pct desc
    ) as monthly_return_rank
from performance