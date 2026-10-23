"""
Find schema.org items that have a "schema:supersededBy" property.

Loads the latest schema.org JSON-LD (via biothings_schema's own loader), walks every
record in the @graph, and lists each item that is superseded along with the value(s)
of its supersededBy property (the term(s) that replace it).

Usage:
    python scripts/find_superseded_items.py                  # latest schema.org version
    python scripts/find_superseded_items.py --version 29.0   # specific version
    python scripts/find_superseded_items.py --output superseded_items.json
"""

import argparse
import json
import os
import sys

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from biothings_schema.dataload import get_schemaorg_version, load_schemaorg  # noqa: E402

SUPERSEDED_KEYS = ("schema:supersededBy", "http://schema.org/supersededBy")


def superseded_values(record):
    """Return the list of supersededBy values for a record (empty if none)."""
    values = []
    for key in SUPERSEDED_KEYS:
        if key not in record:
            continue
        raw = record[key]
        for v in raw if isinstance(raw, list) else [raw]:
            # values are usually {"@id": "schema:X"}, but fall back to the raw value
            values.append(v.get("@id", v) if isinstance(v, dict) else v)
    return values


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

    superseded_items = []
    for record in graph:
        values = superseded_values(record)
        if values:
            superseded_items.append(
                {"@id": record.get("@id"), "type": item_type(record), "supersededBy": values}
            )

    superseded_items.sort(key=lambda x: (x["type"], x["@id"] or ""))
    for item in superseded_items:
        print(f"[{item['type']:8}] {item['@id']}  ->  {', '.join(item['supersededBy'])}")

    # every distinct supersededBy value, and which items point to it
    replacements = {}
    for item in superseded_items:
        for v in item["supersededBy"]:
            replacements.setdefault(v, []).append(item["@id"])

    # replacements that are themselves superseded (chains worth knowing about)
    superseded_ids = {item["@id"] for item in superseded_items}
    chained = sorted(v for v in replacements if v in superseded_ids)

    by_type = {}
    for item in superseded_items:
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1
    print(f"\nTotal items with supersededBy: {len(superseded_items)}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")
    print(f"Distinct supersededBy values: {len(replacements)}")
    for v, ids in sorted(replacements.items()):
        print(f"  {v}  <-  {', '.join(ids)}")
    if chained:
        print(f"\nReplacements that are themselves superseded: {', '.join(chained)}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(
                {
                    "version": version,
                    "count": len(superseded_items),
                    "items": superseded_items,
                    "supersededBy_values": replacements,
                    "chained_replacements": chained,
                },
                f,
                indent=2,
            )
        print(f"\nWrote results to {args.output}")


if __name__ == "__main__":
    main()
