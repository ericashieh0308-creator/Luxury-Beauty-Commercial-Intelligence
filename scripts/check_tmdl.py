"""Detect duplicate properties in TMDL indentation scopes.

This targeted static check skips multiline expressions. Microsoft TOM remains
the authority for TMDL grammar and model deserialization.
"""
from dataclasses import dataclass, field
from pathlib import Path
import re

OBJECT = re.compile(
    r"^(?:database|model|table|column|measure|hierarchy|level|partition|relationship|"
    r"variation|expression|cultureInfo|calculationItem|role|tablePermission|"
    r"perspective|perspectiveTable|perspectiveColumn|perspectiveMeasure|"
    r"perspectiveHierarchy)\s+\S"
)
NAMED_METADATA = re.compile(r"^(annotation|extendedProperty)\s+('(?:[^']|'')+'|\S+?)(?=\s*=|\s*:|$)")
PROPERTY = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)(?:\s*(:|=)\s*(.*))?$")


@dataclass
class Scope:
    depth: int
    name: str
    properties: dict[str, int] = field(default_factory=dict)


def duplicate_properties(text):
    """Yield location and first occurrence for each duplicate in one scope."""
    scopes = [Scope(-1, "document")]
    fenced = False
    expression_depth = None
    for number, line in enumerate(text.removeprefix("\ufeff").splitlines(), 1):
        body = line.lstrip()
        if fenced:
            if body == "```":
                fenced = False
            continue
        if not body or body.startswith("//"):
            continue
        depth = len(line) - len(body)
        if expression_depth is not None:
            if depth > expression_depth:
                continue
            expression_depth = None
        while scopes[-1].depth >= depth:
            scopes.pop()
        parent = scopes[-1]

        if OBJECT.match(body):
            # Object children can reuse the same property names independently.
            scopes.append(Scope(depth, body.split(" = ", 1)[0]))
        else:
            named = NAMED_METADATA.match(body)
            prop = PROPERTY.fullmatch(body)
            if named:
                key = " ".join(named.groups())
            elif prop:
                key = prop[1]
            else:
                continue
            normalized = key.casefold()
            if normalized in parent.properties:
                yield number, key, parent.name, parent.properties[normalized]
            else:
                parent.properties[normalized] = number
            if prop and prop[2] is None:
                # A bare property may own child properties, e.g. dataAccessOptions.
                scopes.append(Scope(depth, body))
            if prop and prop[2] == "=" and not prop[3]:
                expression_depth = depth
        if body.endswith("= ```"):
            fenced = True
        elif OBJECT.match(body) and body.endswith(" ="):
            # Continuation lines for a measure or expression are deeper than its metadata.
            expression_depth = depth + 1


def check_tmdl_tree(model: Path):
    issues = []
    for path in sorted(model.rglob("*.tmdl")):
        text = path.read_text(encoding="utf-8-sig")
        for line, key, scope, first in duplicate_properties(text):
            issues.append(f"{path.relative_to(model)}:{line}: duplicate property {key} in {scope} (first at line {first})")
    if issues:
        raise ValueError("\n".join(issues))
