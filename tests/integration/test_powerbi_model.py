"""Check the source-controlled Power BI model contract."""

from pathlib import Path

MODEL = (
    Path(__file__).resolve().parents[2]
    / "dashboard/powerbi/FX Market Intelligence Dashboard.SemanticModel/definition"
)


def test_date_fields_are_dates_and_star_relationships_are_explicit() -> None:
    date_fields = {
        "tbl_dim_date": ("date_key",),
        "tbl_fact_fx_rates": ("observation_date",),
        "tbl_fact_fx_metrics": ("observation_date",),
        "tbl_fact_macro": ("observation_date", "vintage_date", "release_date"),
    }
    for table, columns in date_fields.items():
        model = (MODEL / "tables" / f"{table}.tmdl").read_text(encoding="utf-8")
        for column in columns:
            section = model.split(f"\tcolumn {column}\n", 1)[1].split("\n\tcolumn ", 1)[0]
            assert "dataType: dateTime" in section, (table, column)
            assert f'{{"{column}", type date}}' in model, (table, column)

    relationships = (MODEL / "relationships.tmdl").read_text(encoding="utf-8")
    expected = {
        ("tbl_fact_fx_rates", "observation_date", "tbl_dim_date", "date_key"),
        ("tbl_fact_fx_metrics", "observation_date", "tbl_dim_date", "date_key"),
        ("tbl_fact_macro", "observation_date", "tbl_dim_date", "date_key"),
        ("tbl_fact_fx_rates", "pair_id", "tbl_dim_fx_pair", "pair_id"),
        ("tbl_fact_fx_metrics", "pair_id", "tbl_dim_fx_pair", "pair_id"),
        ("tbl_fact_fx_rates", "source_id", "tbl_dim_source", "source_id"),
        ("tbl_fact_fx_metrics", "source_id", "tbl_dim_source", "source_id"),
        ("tbl_fact_macro", "source_id", "tbl_dim_source", "source_id"),
        ("tbl_fact_macro", "series_id", "tbl_dim_indicator", "indicator_id"),
    }
    for fact, from_column, dim, to_column in expected:
        assert (f"fromColumn: {fact}.{from_column}\n\ttoColumn: {dim}.{to_column}") in relationships


def test_measures_are_source_aware_and_refresh_visible() -> None:
    measures = (MODEL / "tables" / "tbl_fact_fx_rates.tmdl").read_text(encoding="utf-8")
    for label in ("Latest FX Rate", "Latest Observation Date", "Last Refresh"):
        assert f"measure '{label}'" in measures
    assert "HASONEVALUE" in measures
