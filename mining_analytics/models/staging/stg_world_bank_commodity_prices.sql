
with source_data as (

    select *
    from {{ source('mining', 'world_bank_commodity_prices') }}

),

cleaned as (

    select
        trading_date::date as trading_date,
        upper(symbol) as symbol,
        commodity_name,
        close_price::numeric(18, 4) as close_price,
        unit,
        source as data_source,
        frequency,
        ingested_at::timestamptz as ingested_at

    from source_data

)

select *
from cleaned
