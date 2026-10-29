"""
Find schema.org items that reference https://attic.schema.org/ (deprecated terms).

Loads the latest schema.org JSON-LD (via biothings_schema's own loader), walks every
record in the @graph, and lists each item that mentions "attic.schema.org" anywhere
in its values, along with the field(s) where the reference appears.

Usage:
    python scripts/find_attic_items.py                  # latest schema.org version
    python scripts/find_attic_items.py --version 29.0   # specific version
    python scripts/find_attic_items.py --output attic_items.json
"""

import argparse
import json
import os
import sys

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from biothings_schema.dataload import get_schemaorg_version, load_schemaorg  # noqa: E402

ATTIC_MARKER = "attic.schema.org"


def find_attic_refs(value, path=""):
    """Recursively yield the field paths in `value` whose string values mention the attic."""
    if isinstance(value, str):
        if ATTIC_MARKER in value:
            yield path, value
    elif isinstance(value, dict):
        for key, sub in value.items():
            # keys can be URIs too, so check them as well
            if ATTIC_MARKER in key:
                yield f"{path}.{key}" if path else key, key
            yield from find_attic_refs(sub, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            yield from find_attic_refs(sub, f"{path}[{i}]")


def item_type(record):
    """Classify a record as Class / Property / other based on its @type."""
    types = record.get("@type", [])
    if isinstance(types, str):
        types = [types]
    if "rdfs:Class" in types or "http://www.w3.org/2000/01/rdf-schema#Class" in types:
        return "Class"
    if "rdf:Property" in types or "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property" in types:
        return "Property"
    return ", ".join(types) or "unknown"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", help="schema.org version to load (default: latest)")
    parser.add_argument("--output", help="optional path to write the results as JSON")
    args = parser.parse_args()

    version = args.version or get_schemaorg_version()
    schema = load_schemaorg(version=version, verbose=True)
    graph = schema.get("@graph", [])
    print(f"schema.org version {version}: {len(graph)} records in @graph\n")

    attic_items = []
    for record in graph:
        refs = list(find_attic_refs(record))
        if refs:
            attic_items.append(
                {
                    "@id": record.get("@id"),
                    "type": item_type(record),
                    "references": [{"field": f, "value": v} for f, v in refs],
                }
            )

    attic_items.sort(key=lambda x: (x["type"], x["@id"] or ""))
    for item in attic_items:
        fields = ", ".join(sorted({r["field"] for r in item["references"]}))
        print(f"[{item['type']:8}] {item['@id']}  ({fields})")

    by_type = {}
    for item in attic_items:
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1
    print(f"\nTotal items referencing {ATTIC_MARKER}: {len(attic_items)}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"version": version, "count": len(attic_items), "items": attic_items}, f, indent=2)
        print(f"\nWrote results to {args.output}")


if __name__ == "__main__":
    main()
