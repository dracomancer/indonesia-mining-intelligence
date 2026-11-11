{{ config(materialized='table') }}

with stock_data as (

    select *
    from {{ ref('int_stock_indicators') }}
    where trading_date >= date '2023-01-01'

),

jisdor_data as (

    select
        trading_date,
        currency,
        jisdor_rate,

        lag(jisdor_rate) over (
            partition by currency
            order by trading_date
        ) as previous_jisdor_rate

    from {{ ref('stg_jisdor_rates') }}

),

jisdor_indicators as (

    select
        trading_date,
        currency,
        jisdor_rate,
        previous_jisdor_rate,

        jisdor_rate - previous_jisdor_rate
            as jisdor_change,

        case
            when previous_jisdor_rate is not null
                 and previous_jisdor_rate <> 0
            then (
                (jisdor_rate - previous_jisdor_rate)
                / previous_jisdor_rate
            ) * 100
        end as jisdor_change_pct

    from jisdor_data

),

macro_data as (

    select
        s.trading_date,
        s.symbol,

        s.close_price,
        s.daily_return_pct,
        s.volatility_20d,

        j.currency,
        j.jisdor_rate,
        j.previous_jisdor_rate,
        j.jisdor_change,
        j.jisdor_change_pct,

        b.policy_rate,
        b.effective_date as bi_rate_effective_date,

        (
            select previous.policy_rate
            from {{ ref('stg_bi_policy_rates') }} previous
            where previous.effective_date < b.effective_date
            order by previous.effective_date desc
            limit 1
        ) as previous_policy_rate

    from stock_data s

    left join jisdor_indicators j
        on s.trading_date = j.trading_date
       and j.currency = 'USD'

    left join lateral (
        select
            policy_rate,
            effective_date
        from {{ ref('stg_bi_policy_rates') }}
        where effective_date <= s.trading_date
        order by effective_date desc
        limit 1
    ) b on true

),

final as (

    select
        *,

        (policy_rate - previous_policy_rate) * 100
            as bi_rate_decision_change_bps,

        case
            when jisdor_rate is not null
                 and close_price is not null
            then true
            else false
        end as has_macro_data

    from macro_data

)

select *
from final
