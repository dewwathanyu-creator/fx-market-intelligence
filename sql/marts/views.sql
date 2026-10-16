CREATE OR REPLACE VIEW v_fx_latest AS
SELECT *
FROM fact_fx_rates
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY source_id, pair_id, rate_type
    ORDER BY observation_date DESC
) = 1;

CREATE OR REPLACE VIEW v_macro_latest AS
SELECT *
FROM fact_macro
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY source_id, series_id
    ORDER BY observation_date DESC, vintage_date DESC NULLS LAST
) = 1;
