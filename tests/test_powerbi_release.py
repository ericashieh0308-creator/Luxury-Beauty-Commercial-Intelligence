from pathlib import Path

import pytest

from scripts.prepare_powerbi import BLANK_PARAMETER, prepare
from scripts.validate_powerbi import CANDIDATES, project_paths, validate_variations


@pytest.mark.parametrize("candidate,visuals", [("optimized", 76), ("fallback", 67)])
def test_prepare_isolated_candidate(tmp_path, candidate, visuals):
    _, original_model = project_paths(CANDIDATES[candidate])
    original = (original_model / "expressions.tmdl").read_bytes()

    result = prepare(candidate, tmp_path)
    assert result["pages"] == 10 and result["visuals"] == visuals
    session = Path(result["pbip"]).parent
    report, model = project_paths(session)
    assert report.parent == model.parent.parent == session
    expression = (model / "expressions.tmdl").read_text(encoding="utf-8")
    assert BLANK_PARAMETER not in expression and result["demo_root"] in expression
    assert (Path(result["demo_root"]) / "finance" / "fact_simulated_finance.csv").is_file()
    assert (original_model / "expressions.tmdl").read_bytes() == original


@pytest.mark.parametrize("candidate", CANDIDATES)
def test_orphaned_hidden_date_table_is_rejected(candidate):
    _, model = project_paths(CANDIDATES[candidate])
    tables = {path.stem: path.read_text(encoding="utf-8-sig") for path in (model / "tables").glob("*.tmdl")}
    relationships = (model / "relationships.tmdl").read_text(encoding="utf-8-sig")
    # Reproduce the previous regression while retaining the relationship and hierarchy.
    source, variation = tables["assortment_counts"].split("\n\t\tvariation Variation\n", 1)
    tables["assortment_counts"] = source + "\n\n" + variation.split("\n\n", 1)[1]
    with pytest.raises(ValueError, match="ShowAsVariationsOnly has no incoming variation"):
        validate_variations(tables, relationships)
