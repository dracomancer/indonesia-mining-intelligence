with source_data as (

    select
        (to_jsonb(c)->>'Date')::date as trading_date,
        symbol,
        commodity_name,
        category,
        unit,
        (to_jsonb(c)->>'Close')::double precision as close_price,
        daily_return_pct::double precision as daily_return_pct,
        source as data_source

    from {{ source('mining', 'commodity_prices') }} c

),

cleaned as (

    select
        trading_date,
        symbol,
        commodity_name,
        category,
        unit,
        close_price,

        nullif(
            daily_return_pct,
            'NaN'::double precision
        ) as daily_return_pct,

        data_source

    from source_data

    where symbol in ('BRENT', 'COPPER', 'GOLD')

)

select *
from cleaned
