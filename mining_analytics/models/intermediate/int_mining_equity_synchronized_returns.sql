{{ config(materialized='table') }}

with common_dates as (
    select distinct trading_date
    from {{ ref('int_mining_equity_multifactor') }}
    where brent_close is not null
      and copper_close is not null
      and gold_close is not null
),

date_intervals as (
    select
        trading_date,
        lag(trading_date) over (order by trading_date) as previous_common_date
    from common_dates
),

intervals as (
    select
        trading_date,
        previous_common_date,
        trading_date - previous_common_date as calendar_gap_days
    from date_intervals
    where previous_common_date is not null
),

current_data as (
    select *
    from {{ ref('int_mining_equity_multifactor') }}
),

previous_data as (
    select *
    from current_data
),

aligned_data as (
    select
        current.symbol,
        current.trading_date,
        previous.trading_date as previous_trading_date,
        intervals.calendar_gap_days,

        current.close_price as stock_close,
        previous.close_price as previous_stock_close,

        current.brent_close,
        previous.brent_close as previous_brent_close,

        current.copper_close,
        previous.copper_close as previous_copper_close,

        current.gold_close,
        previous.gold_close as previous_gold_close,

        current.jisdor_rate,
        previous.jisdor_rate as previous_jisdor_rate,

        current.policy_rate,
        previous.policy_rate as previous_policy_rate

    from intervals
    join current_data current
        on current.trading_date = intervals.trading_date
    join previous_data previous
        on previous.symbol = current.symbol
       and previous.trading_date = intervals.previous_common_date
),

final as (
    select
        *,
        100.0 * (stock_close / nullif(previous_stock_close, 0) - 1)
            as stock_return_pct,

        100.0 * (brent_close / nullif(previous_brent_close, 0) - 1)
            as brent_return_pct,

        100.0 * (copper_close / nullif(previous_copper_close, 0) - 1)
            as copper_return_pct,

        100.0 * (gold_close / nullif(previous_gold_close, 0) - 1)
            as gold_return_pct,

        100.0 * (jisdor_rate / nullif(previous_jisdor_rate, 0) - 1)
            as jisdor_return_pct,

        100.0 * (policy_rate - previous_policy_rate)
            as bi_rate_change_bps

    from aligned_data
)

select *
from final
where stock_close is not null
  and previous_stock_close is not null
  and stock_close > 0
  and previous_stock_close > 0
  and brent_close > 0
  and previous_brent_close > 0
  and copper_close > 0
  and previous_copper_close > 0
  and gold_close > 0
  and previous_gold_close > 0
  and jisdor_rate > 0
  and previous_jisdor_rate > 0
