with source_data as (

    select *
    from {{ source('mining', 'bi_policy_rates') }}

),

renamed as (

    select
        effective_date::date as effective_date,
        policy_rate::numeric(5, 2) as policy_rate,
        source as data_source,
        ingested_at::timestamptz as ingested_at

    from source_data

)

select *
from renamed
