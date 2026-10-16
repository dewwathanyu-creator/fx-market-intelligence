SELECT 'fact_fx_rates' AS table_name, COUNT(*) AS row_count FROM fact_fx_rates
UNION ALL
SELECT 'fact_macro' AS table_name, COUNT(*) AS row_count FROM fact_macro;
