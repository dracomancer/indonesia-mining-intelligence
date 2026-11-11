{{ config(materialized='table') }}

with price_data as (
    select
        symbol,
        ((to_jsonb(s)->>'Date')::timestamptz
            at time zone 'Asia/Jakarta')::date as trading_date,
        (to_jsonb(s)->>'Close')::numeric as close_price,
        (to_jsonb(s)->>'Adj Close')::numeric as adjusted_close,
        coalesce(
            (to_jsonb(s)->>'Dividends')::numeric,
            0
        ) as dividends
    from {{ source('mining', 'stock_prices') }} s
),

aligned_returns as (
    select
        r.symbol,
        r.previous_trading_date,
        r.trading_date,

        nullif(
            r.stock_return_pct::double precision,
            'NaN'::double precision
        ) as raw_return_pct,

        p_current.close_price,
        p_previous.close_price as previous_close_price,

        p_current.adjusted_close,
        p_previous.adjusted_close as previous_adjusted_close,

        coalesce(d.dividend_amount, 0) as dividend_amount

    from {{ ref('int_mining_equity_synchronized_returns') }} r

    left join price_data p_current
        on r.symbol = p_current.symbol
        and r.trading_date = p_current.trading_date

    left join price_data p_previous
        on r.symbol = p_previous.symbol
        and r.previous_trading_date = p_previous.trading_date

    left join lateral (
        select
            sum(p.dividends) as dividend_amount
        from price_data p
        where p.symbol = r.symbol
          and p.trading_date > r.previous_trading_date
          and p.trading_date <= r.trading_date
    ) d on true
),

calculated_returns as (
    select
        *,
        case
            when previous_adjusted_close is not null
             and previous_adjusted_close <> 0
             and adjusted_close is not null
            then
                100.0 * (
                    adjusted_close / previous_adjusted_close - 1
                )
            else null
        end as total_return_pct

    from aligned_returns
),

final as (
    select
        symbol,
        previous_trading_date,
        trading_date,

        raw_return_pct,
        total_return_pct,

        dividend_amount,

        total_return_pct - raw_return_pct
            as dividend_adjustment_pp,

        case
            when dividend_amount > 0 then true
            else false
        end as has_dividend,

        close_price,
        previous_close_price,
        adjusted_close,
        previous_adjusted_close

    from calculated_returns
)

select *
from final
