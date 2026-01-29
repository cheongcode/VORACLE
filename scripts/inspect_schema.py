#!/usr/bin/env python3
"""Inspect the GRID GraphQL schema."""
import json
from pathlib import Path

schema_path = Path(__file__).parent.parent / "packages/core/grid/schema/schema.json"
schema = json.loads(schema_path.read_text())

def get_type_str(type_obj):
    if type_obj.get("name"):
        return type_obj["name"]
    kind = type_obj.get("kind", "")
    of_type = type_obj.get("ofType", {})
    inner = get_type_str(of_type) if of_type else "?"
    return f"{kind}[{inner}]"

print("=" * 60)
print("TEAMS QUERY STRUCTURE")
print("=" * 60)

for t in schema["__schema"]["types"]:
    if t["name"] == "Query":
        for f in t["fields"]:
            if f["name"] == "teams":
                print("\nQuery: teams")
                print("Arguments:")
                for arg in f["args"]:
                    print(f"  - {arg['name']}: {get_type_str(arg['type'])}")
                break

# Find Team type
print("\n" + "=" * 60)
print("TEAM TYPE FIELDS")
print("=" * 60)

for t in schema["__schema"]["types"]:
    if t["name"] == "Team":
        for f in t.get("fields", []):
            print(f"  - {f['name']}: {get_type_str(f['type'])}")
        break

# Find allSeries query
print("\n" + "=" * 60)
print("ALL_SERIES QUERY")
print("=" * 60)

for t in schema["__schema"]["types"]:
    if t["name"] == "Query":
        for f in t["fields"]:
            if f["name"] == "allSeries":
                print("Arguments:")
                for arg in f["args"]:
                    print(f"  - {arg['name']}: {get_type_str(arg['type'])}")
                break

# Find SeriesFilter type
print("\n" + "=" * 60)
print("SERIES FILTER FIELDS")
print("=" * 60)

for t in schema["__schema"]["types"]:
    if t["name"] == "SeriesFilter":
        for f in t.get("inputFields", []):
            print(f"  - {f['name']}: {get_type_str(f['type'])}")
        break

# Find StringFilter type
print("\n" + "=" * 60)
print("STRING FILTER FIELDS")
print("=" * 60)

for t in schema["__schema"]["types"]:
    if t["name"] == "StringFilter":
        for f in t.get("inputFields", []):
            print(f"  - {f['name']}: {get_type_str(f['type'])}")
        break
