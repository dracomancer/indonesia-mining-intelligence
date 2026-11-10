
with source_data as (

    select *
    from {{ source('mining', 'stock_prices') }}

),

renamed as (

    select
        "Date" as price_timestamp,
        trading_date::date as trading_date,

        symbol,
        "Open" as open_price,
        "High" as high_price,
        "Low" as low_price,
        "Close" as close_price,
        "Adj Close" as adjusted_close,
        "Volume" as volume,

        "Dividends" as dividends,
        "Stock Splits" as stock_splits,

        daily_return_pct,
        intraday_range_pct,
        turnover_idr,

        source as data_source,
        ingested_at::timestamptz as ingested_at,

        market,
        exchange,
        currency

    from source_data

)

select * from renamed
