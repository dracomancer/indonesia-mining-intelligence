
with historical_data as (

    select
        trading_date,
        symbol,
        close_price,
        adjusted_close

    from {{ ref('mart_stock_history') }}

),

latest_prices as (

    select distinct on (symbol)
        symbol,
        trading_date as latest_date,
        close_price as latest_close,
        adjusted_close as latest_adjusted_close

    from historical_data

    order by symbol, trading_date desc

),

historical_returns as (

    select
        latest.symbol,
        latest.latest_date,
        latest.latest_close,
        latest.latest_adjusted_close,

        month_1.adjusted_close as price_1m,
        month_3.adjusted_close as price_3m,
        month_6.adjusted_close as price_6m,
        year_1.adjusted_close as price_1y

    from latest_prices latest

    left join lateral (
        select adjusted_close
        from historical_data h
        where h.symbol = latest.symbol
          and h.trading_date <= latest.latest_date - interval '1 month'
        order by h.trading_date desc
        limit 1
    ) month_1 on true

    left join lateral (
        select adjusted_close
        from historical_data h
        where h.symbol = latest.symbol
          and h.trading_date <= latest.latest_date - interval '3 months'
        order by h.trading_date desc
        limit 1
    ) month_3 on true

    left join lateral (
        select adjusted_close
        from historical_data h
        where h.symbol = latest.symbol
          and h.trading_date <= latest.latest_date - interval '6 months'
        order by h.trading_date desc
        limit 1
    ) month_6 on true

    left join lateral (
        select adjusted_close
        from historical_data h
        where h.symbol = latest.symbol
          and h.trading_date <= latest.latest_date - interval '1 year'
        order by h.trading_date desc
        limit 1
    ) year_1 on true

)

select
    symbol,
    latest_date,
    latest_close,

    round(
        (
            (latest_adjusted_close / nullif(price_1m, 0) - 1) * 100
        )::numeric,
        2
    ) as return_1m_pct,

    round(
        (
            (latest_adjusted_close / nullif(price_3m, 0) - 1) * 100
        )::numeric,
        2
    ) as return_3m_pct,

    round(
        (
            (latest_adjusted_close / nullif(price_6m, 0) - 1) * 100
        )::numeric,
        2
    ) as return_6m_pct,

    round(
        (
            (latest_adjusted_close / nullif(price_1y, 0) - 1) * 100
        )::numeric,
        2
    ) as return_1y_pct

from historical_returns
