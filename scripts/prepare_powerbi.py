"""Prepare an isolated local Power BI working copy using the public demo."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

from beauty.demo import build_catalog, export_finance
from scripts.validate_powerbi import (
    CANDIDATES, ROOT, project_paths, validate_finance, validate_layout, validate_model,
)

BLANK_PARAMETER = 'expression DemoRoot = "" meta'


def prepare(candidate, output):
    project = CANDIDATES[candidate]
    report, model = project_paths(project)
    optimized = candidate == "optimized"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".preparing-", dir=output) as work:
        staging = Path(work) / "release"
        demo = staging / "demo"
        build_catalog(demo / "catalog")
        export_finance(demo / "finance")
        fields = validate_model(model, demo, optimized=optimized)
        pages = validate_layout(report, fields, optimized=optimized)
        validate_finance(demo)

        pbip, = project.glob("*.pbip")
        shutil.copy2(pbip, staging / pbip.name)
        ignore = shutil.ignore_patterns(".pbi", "*.abf", "*.pbix", "localSettings.json")
        shutil.copytree(report, staging / report.name, ignore=ignore)
        shutil.copytree(model.parent, staging / model.parent.name, ignore=ignore)
        staged_report, staged_model = project_paths(staging)
        validate_layout(staged_report, fields, optimized=optimized)

        destination = Path(tempfile.mkdtemp(prefix=f"{candidate}-", dir=output))
        # Update only the disposable copy, so Desktop saves cannot touch the repository sources.
        expressions = staged_model / "expressions.tmdl"
        source = expressions.read_text(encoding="utf-8-sig")
        demo_root = (destination / "demo").resolve().as_posix()
        m_literal = demo_root.replace('"', '""').replace("#(", "#(#)(")
        if source.count(BLANK_PARAMETER) != 1:
            raise ValueError("Expected exactly one blank DemoRoot parameter")
        expressions.write_text(source.replace(BLANK_PARAMETER, f'expression DemoRoot = "{m_literal}" meta'),
                               encoding="utf-8")
        for item in staging.iterdir():
            item.rename(destination / item.name)
    return {"pbip": str((destination / pbip.name).resolve()), "demo_root": demo_root,
            "pages": len(pages), "visuals": sum(count for _, count in pages)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", choices=CANDIDATES, default="optimized")
    args = parser.parse_args()
    print(json.dumps(prepare(args.candidate, ROOT / "output/powerbi-sessions")))


if __name__ == "__main__":
    main()
