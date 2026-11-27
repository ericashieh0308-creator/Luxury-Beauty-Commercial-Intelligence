from beauty.demo import build_catalog
from beauty.finance_export import build as export_finance
from scripts.validate_powerbi import project_paths, validate_finance, validate_layout, validate_model


def test_powerbi_demo_project(tmp_path):
    build_catalog(tmp_path / "catalog")
    export_finance(tmp_path / "finance")
    report, model = project_paths()
    fields = validate_model(model, tmp_path)
    pages = validate_layout(report, fields)
    assert pages[0][0] == "Executive Overview"
    assert pages[-1][0] == "Data Quality & Methodology"
    assert all(visual_count >= 5 for _, visual_count in pages)
    validate_finance(tmp_path)
