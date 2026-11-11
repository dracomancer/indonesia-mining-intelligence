with source_data as (

    select *
    from {{ source('mining', 'jisdor_rates') }}

),

renamed as (

    select
        trading_date::date as trading_date,
        currency,
        nominal::numeric(12, 2) as nominal,
        jisdor_rate::numeric(15, 2) as jisdor_rate,
        buy_rate::numeric(15, 2) as buy_rate,
        sell_rate::numeric(15, 2) as sell_rate,
        source as data_source,
        ingested_at::timestamptz as ingested_at

    from source_data

)

select *
from renamed
