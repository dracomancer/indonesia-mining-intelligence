{{ config(materialized='table') }}

with stock_macro_data as (

    select *
    from {{ ref('int_macro_market_indicators') }}

),

commodity_pivot as (

    select
        trading_date,

        max(close_price) filter (
            where symbol = 'BRENT'
        ) as brent_close,

        max(daily_return_pct) filter (
            where symbol = 'BRENT'
        ) as brent_return_pct,

        max(close_price) filter (
            where symbol = 'COPPER'
        ) as copper_close,

        max(daily_return_pct) filter (
            where symbol = 'COPPER'
        ) as copper_return_pct,

        max(close_price) filter (
            where symbol = 'GOLD'
        ) as gold_close,

        max(daily_return_pct) filter (
            where symbol = 'GOLD'
        ) as gold_return_pct

    from {{ ref('stg_commodity_market_factors') }}

    group by trading_date

),

combined as (

    select
        s.*,

        c.brent_close,
        c.brent_return_pct,

        c.copper_close,
        c.copper_return_pct,

        c.gold_close,
        c.gold_return_pct

    from stock_macro_data s

    left join commodity_pivot c
        on s.trading_date = c.trading_date

),

final as (

    select
        *,

        case
            when brent_return_pct is not null
             and copper_return_pct is not null
             and gold_return_pct is not null
            then true
            else false
        end as has_complete_commodity_returns,

        case
            when daily_return_pct is not null
             and daily_return_pct::text <> 'NaN'
             and jisdor_change_pct is not null
             and brent_return_pct is not null
             and copper_return_pct is not null
             and gold_return_pct is not null
            then true
            else false
        end as has_complete_daily_factor_data

    from combined

)

select *
from final
