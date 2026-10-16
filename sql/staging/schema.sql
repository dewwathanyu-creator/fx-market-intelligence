CREATE TABLE IF NOT EXISTS dim_date (
    date_key DATE PRIMARY KEY,
    calendar_date DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_currency (
    currency_code VARCHAR PRIMARY KEY,
    region VARCHAR
);
CREATE TABLE IF NOT EXISTS dim_fx_pair (
    pair_id VARCHAR PRIMARY KEY,
    base_ccy VARCHAR NOT NULL,
    quote_ccy VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_indicator (
    indicator_id VARCHAR PRIMARY KEY,
    unit VARCHAR NOT NULL,
    frequency VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_source (
    source_id VARCHAR PRIMARY KEY,
    provider VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_fx_rates (
    source_id VARCHAR NOT NULL,
    series_id VARCHAR NOT NULL,
    pair_id VARCHAR NOT NULL,
    observation_date DATE NOT NULL,
    rate_type VARCHAR NOT NULL,
    rate DECIMAL(20, 10) NOT NULL,
    unit VARCHAR NOT NULL,
    frequency VARCHAR NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source_id, series_id, observation_date, rate_type)
);
CREATE TABLE IF NOT EXISTS fact_macro (
    source_id VARCHAR NOT NULL,
    series_id VARCHAR NOT NULL,
    observation_date DATE NOT NULL,
    vintage_key VARCHAR NOT NULL,
    vintage_date DATE,
    release_date DATE,
    value DECIMAL(20, 10),
    unit VARCHAR NOT NULL,
    frequency VARCHAR NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source_id, series_id, observation_date, vintage_key)
);
CREATE TABLE IF NOT EXISTS fact_fx_analytics (
    pair_id VARCHAR NOT NULL,
    observation_date DATE NOT NULL,
    metric VARCHAR NOT NULL,
    window_size INTEGER NOT NULL,
    metric_value DOUBLE,
    method_version VARCHAR NOT NULL,
    PRIMARY KEY (pair_id, observation_date, metric, window_size, method_version)
);
CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id VARCHAR PRIMARY KEY,
    run_at TIMESTAMPTZ NOT NULL,
    status VARCHAR NOT NULL,
    fx_count INTEGER NOT NULL,
    macro_count INTEGER NOT NULL,
    error_message VARCHAR
);
