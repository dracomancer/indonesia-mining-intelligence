
with source_data as (

    select *
    from {{ source('mining', 'commodity_prices') }}

),

renamed as (

    select
        "Date" as price_timestamp,

        -- Preserve the commodity's New York trading date
        ("Date" at time zone 'America/New_York')::date
            as trading_date,

        symbol,
        commodity_name,
        category,
        unit,

        "Open" as open_price,
        "High" as high_price,
        "Low" as low_price,
        "Close" as close_price,
        "Adj Close" as adjusted_close,
        "Volume" as volume,

        "Dividends" as dividends,
        "Stock Splits" as stock_splits,

        price_change,
        daily_return_pct,
        intraday_range_pct,
        sma_20,
        sma_50,
        volatility_20d,

        source as data_source,
        ingested_at,
        ingestion_processed_at,

        market

    from source_data

)

select *
from renamed
