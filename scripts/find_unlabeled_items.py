"""
Find schema.org items that have no "rdfs:label" property.

Loads the latest raw schema.org JSON-LD (bypassing load_schemaorg, which drops non "schema:"
records), walks every record in the @graph, and lists each item missing an rdfs:label. In recent releases these
are stub records for terms from external vocabularies (e.g. bibo, fibo, gs1, unece) that
schema.org terms map to via owl:equivalentClass, rdfs:subClassOf, skos:exactMatch, etc.
Items are exported exactly as they appear in the source @graph; the schema.org records that
reference each one (and through which field) are listed separately under "referenced_by".

Usage:
    python scripts/find_unlabeled_items.py                  # latest schema.org version
    python scripts/find_unlabeled_items.py --version 29.0   # specific version
    python scripts/find_unlabeled_items.py --output unlabeled_items.json
"""

import argparse
import json
import os
import sys

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from biothings_schema.dataload import (  # noqa: E402
    construct_schemaorg_url,
    get_schemaorg_version,
    load_json_or_yaml,
)

LABEL_KEYS = ("rdfs:label", "http://www.w3.org/2000/01/rdf-schema#label")


def has_label(record):
    """Return True if the record has an rdfs:label (in curie or uri form)."""
    return any(key in record for key in LABEL_KEYS)


def find_id_refs(value, field=None):
    """Recursively yield (field, @id) pairs for every {"@id": ...} reference in `value`."""
    if isinstance(value, dict):
        if field is not None and "@id" in value:
            yield field, value["@id"]
        for key, sub in value.items():
            if key != "@id":
                yield from find_id_refs(sub, key)
    elif isinstance(value, list):
        for sub in value:
            yield from find_id_refs(sub, field)


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


def id_prefix(_id):
    """Return the curie prefix of an @id (or the whole value if it's a full URI)."""
    if not _id:
        return "unknown"
    if _id.startswith(("http://", "https://")):
        return _id
    return _id.split(":", 1)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", help="schema.org version to load (default: latest)")
    parser.add_argument("--output", help="optional path to write the results as JSON")
    args = parser.parse_args()

    version = args.version or get_schemaorg_version()
    # load the raw file: load_schemaorg filters out the (non "schema:") items we're looking for
    url = construct_schemaorg_url(version)
    print(f"Loading Schema.org schema from {url}")
    schema = load_json_or_yaml(url)
    graph = schema.get("@graph", [])
    print(f"schema.org version {version}: {len(graph)} records in @graph\n")

    # keep the original records untouched (in @graph order)
    unlabeled_items = [record for record in graph if not has_label(record)]
    unlabeled_ids = {record.get("@id") for record in unlabeled_items}

    # which (labeled) records point to the unlabeled items, and through which field
    referenced_by = {_id: [] for _id in unlabeled_ids}
    for record in graph:
        if not has_label(record):
            continue
        for field, ref_id in find_id_refs(record):
            if ref_id in unlabeled_ids:
                referenced_by[ref_id].append({"@id": record.get("@id"), "field": field})

    for record in unlabeled_items:
        refs = ", ".join(f"{r['@id']} ({r['field']})" for r in referenced_by[record.get("@id")]) or "-"
        print(f"[{item_type(record):8}] {record.get('@id')}  <-  {refs}")

    by_type = {}
    by_prefix = {}
    by_field = {}
    for record in unlabeled_items:
        t = item_type(record)
        p = id_prefix(record.get("@id"))
        by_type[t] = by_type.get(t, 0) + 1
        by_prefix[p] = by_prefix.get(p, 0) + 1
        for r in referenced_by[record.get("@id")]:
            by_field[r["field"]] = by_field.get(r["field"], 0) + 1
    unreferenced = [record.get("@id") for record in unlabeled_items if not referenced_by[record.get("@id")]]

    print(f"\nTotal items without rdfs:label: {len(unlabeled_items)}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")
    print(f"By prefix: {len(by_prefix)}")
    for p, n in sorted(by_prefix.items()):
        print(f"  {p}: {n}")
    print("Referenced through:")
    for field, n in sorted(by_field.items(), key=lambda x: -x[1]):
        print(f"  {field}: {n}")
    if unreferenced:
        print(f"\nItems not referenced by any labeled record: {', '.join(unreferenced)}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(
                {
                    "version": version,
                    "count": len(unlabeled_items),
                    "items": unlabeled_items,
                    "referenced_by": referenced_by,
                    "by_prefix": by_prefix,
                    "referenced_through": by_field,
                    "unreferenced": unreferenced,
                },
                f,
                indent=2,
            )
        print(f"\nWrote results to {args.output}")


if __name__ == "__main__":
    main()
