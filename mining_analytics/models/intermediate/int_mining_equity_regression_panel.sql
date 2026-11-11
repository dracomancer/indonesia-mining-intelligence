
{{ config(materialized='table') }}

with synchronized_data as (

    select *
    from {{ ref('int_mining_equity_synchronized_returns') }}

),

total_returns as (

    select
        symbol,
        previous_trading_date,
        trading_date,
        total_return_pct,
        raw_return_pct,
        dividend_amount,
        has_dividend
    from {{ ref('int_mining_equity_total_returns') }}

),

joined_data as (

    select
        s.symbol,
        s.previous_trading_date,
        s.trading_date,
        s.calendar_gap_days,

        -- Dependent variables
        t.total_return_pct,
        t.raw_return_pct,
        t.dividend_amount,
        t.has_dividend,

        -- Commodity factors
        s.brent_return_pct,
        s.copper_return_pct,
        s.gold_return_pct,

        -- Macroeconomic factors
        s.jisdor_return_pct,
        s.bi_rate_change_bps,

        -- Price references
        s.stock_close,
        s.previous_stock_close

    from synchronized_data s

    inner join total_returns t
        on s.symbol = t.symbol
        and s.previous_trading_date = t.previous_trading_date
        and s.trading_date = t.trading_date

)

select *
from joined_data
where total_return_pct is not null
  and brent_return_pct is not null
  and copper_return_pct is not null
  and gold_return_pct is not null
  and jisdor_return_pct is not null
  and bi_rate_change_bps is not null
