import pytest

from scripts.check_tmdl import check_tmdl_tree, duplicate_properties


@pytest.mark.parametrize("declaration,property_name,first,second", [
    ("table Catalog", "lineageTag", "a", "b"),
    ("column Snapshot", "formatString", "yyyy-MM-dd", "General Date"),
    ("measure Revenue = SUM(Sales[Revenue])", "formatString", "0", "#,0"),
    ("hierarchy Calendar", "lineageTag", "a", "b"),
    ("level Month", "column", "Calendar.Month", "Calendar.MonthName"),
    ("partition Catalog = m", "mode", "import", "directQuery"),
    ("relationship DateLink", "fromColumn", "Sales.Date", "Sales.Month"),
])
def test_duplicate_properties_in_same_object(declaration, property_name, first, second):
    model = f"{declaration}\n\t{property_name}: {first}\n\n\t{property_name}: {second}\n"
    assert list(duplicate_properties(model)) == [(4, property_name, declaration.split(" = ")[0], 2)]


def test_reported_hidden_date_error(tmp_path):
    model = tmp_path / "tables"
    model.mkdir()
    file = model / "DateTableTemplate_01f7a383-b1de-4707-a2de-e5fea1e3a7b4.tmdl"
    file.write_text(
        "table DateTableTemplate_01f7a383-b1de-4707-a2de-e5fea1e3a7b4\n"
        "\tisHidden\n\tisPrivate\n\tlineageTag: template\n\n"
        "\tcolumn Date\n\t\tdataType: dateTime\n\t\tformatString: yyyy-MM-dd\n"
        "\t\tisHidden\n\t\tformatString: General Date\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match=r":10: duplicate property formatString in column Date \(first at line 8\)"):
        check_tmdl_tree(tmp_path)


def test_independent_scopes_and_multiline_code():
    model = """table Catalog
\tcolumn First
\t\tformatString: #,0
\t\tannotation Source = CSV
\tcolumn Second
\t\tformatString: #,0
\t\tannotation Source = CSV
\t\tannotation Precision = Whole
\tpartition Catalog = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tmode: simulated code
\t\t\t\tmode: simulated code
\t\t\tin
\t\t\t\tCatalog
"""
    assert list(duplicate_properties(model)) == []
