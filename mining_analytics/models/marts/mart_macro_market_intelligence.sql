with daily_data as (

    select
        *,
        lag(bi_rate_effective_date) over (
            partition by symbol
            order by trading_date
        ) as previous_bi_rate_effective_date

    from {{ ref('int_macro_market_indicators') }}

),

fx_metrics as (

    select
        symbol,

        count(*) as trading_observations,
        min(trading_date) as first_trading_date,
        max(trading_date) as last_trading_date,

        avg(nullif(daily_return_pct::double precision, 'NaN'::double precision))
            as avg_daily_return_pct,

        stddev_samp(
            nullif(daily_return_pct::double precision, 'NaN'::double precision)
        ) as stock_volatility,

        count(jisdor_change_pct) as fx_observations,

        corr(
            nullif(daily_return_pct::double precision, 'NaN'::double precision),
            jisdor_change_pct::double precision
        ) as fx_return_correlation,

        case
            when var_samp(jisdor_change_pct::double precision) > 0
            then
                covar_samp(
                    nullif(daily_return_pct::double precision, 'NaN'::double precision),
                    jisdor_change_pct::double precision
                )
                /
                var_samp(jisdor_change_pct::double precision)
        end as fx_beta

    from daily_data
    group by symbol

),

bi_rate_events as (

    select *
    from daily_data
    where previous_bi_rate_effective_date is not null
      and bi_rate_effective_date
          <> previous_bi_rate_effective_date

),

bi_rate_metrics as (

    select
        symbol,

        count(*) as bi_rate_event_count,

        avg(
            nullif(daily_return_pct::double precision, 'NaN'::double precision)
        ) as avg_return_on_bi_rate_event_days,

        corr(
            nullif(daily_return_pct::double precision, 'NaN'::double precision),
            bi_rate_decision_change_bps::double precision
        ) as bi_rate_event_return_correlation,

        count(*) filter (
            where bi_rate_decision_change_bps > 0
        ) as bi_rate_hike_events,

        count(*) filter (
            where bi_rate_decision_change_bps < 0
        ) as bi_rate_cut_events

    from bi_rate_events
    group by symbol

),

final as (

    select
        fx.symbol,
        fx.trading_observations,
        fx.first_trading_date,
        fx.last_trading_date,

        fx.avg_daily_return_pct,
        fx.stock_volatility,

        fx.fx_observations,
        fx.fx_return_correlation,
        fx.fx_beta,

        coalesce(bi.bi_rate_event_count, 0)
            as bi_rate_event_count,

        bi.avg_return_on_bi_rate_event_days,
        bi.bi_rate_event_return_correlation,

        coalesce(bi.bi_rate_hike_events, 0)
            as bi_rate_hike_events,

        coalesce(bi.bi_rate_cut_events, 0)
            as bi_rate_cut_events

    from fx_metrics fx

    left join bi_rate_metrics bi
        on fx.symbol = bi.symbol

)

select *
from final
