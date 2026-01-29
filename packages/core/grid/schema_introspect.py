"""
GRID GraphQL Schema Introspection

Utilities for fetching, saving, and exploring the GRID GraphQL schema.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def save_schema(schema: dict[str, Any], path: str | Path) -> None:
    """
    Save schema to JSON file.
    
    Args:
        schema: Schema introspection result.
        path: Output file path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    
    logger.info(f"Schema saved to {path}")


def load_schema(path: str | Path) -> dict[str, Any]:
    """
    Load schema from JSON file.
    
    Args:
        path: Schema file path.
        
    Returns:
        Schema dictionary.
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    logger.info(f"Schema loaded from {path}")
    return schema


def get_type_fields(schema: dict[str, Any], type_name: str) -> list[dict[str, Any]]:
    """
    Get fields for a specific type from the schema.
    
    Args:
        schema: Schema introspection result.
        type_name: Name of the type to look up.
        
    Returns:
        List of field definitions.
    """
    types = schema.get("__schema", {}).get("types", [])
    
    for t in types:
        if t.get("name") == type_name:
            fields = t.get("fields", [])
            logger.debug(f"Found {len(fields)} fields for type '{type_name}'")
            return fields
    
    logger.warning(f"Type '{type_name}' not found in schema")
    return []


def get_type_names(schema: dict[str, Any], kind: Optional[str] = None) -> list[str]:
    """
    Get all type names from the schema.
    
    Args:
        schema: Schema introspection result.
        kind: Optional filter by kind (e.g., "OBJECT", "INPUT_OBJECT").
        
    Returns:
        List of type names.
    """
    types = schema.get("__schema", {}).get("types", [])
    
    names = []
    for t in types:
        if t.get("name", "").startswith("__"):
            continue  # Skip internal types
        if kind is None or t.get("kind") == kind:
            names.append(t.get("name"))
    
    return sorted(names)


def find_type_by_name(schema: dict[str, Any], type_name: str) -> Optional[dict[str, Any]]:
    """
    Find a type definition by name.
    
    Args:
        schema: Schema introspection result.
        type_name: Name of the type to find.
        
    Returns:
        Type definition or None.
    """
    types = schema.get("__schema", {}).get("types", [])
    
    for t in types:
        if t.get("name") == type_name:
            return t
    
    return None


def get_query_fields(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Get all top-level query fields.
    
    Args:
        schema: Schema introspection result.
        
    Returns:
        List of query field definitions.
    """
    query_type_name = schema.get("__schema", {}).get("queryType", {}).get("name", "Query")
    return get_type_fields(schema, query_type_name)


def explore_type_tree(
    schema: dict[str, Any],
    type_name: str,
    depth: int = 2,
    visited: Optional[set] = None,
) -> dict[str, Any]:
    """
    Explore a type and its nested fields recursively.
    
    Args:
        schema: Schema introspection result.
        type_name: Starting type name.
        depth: Maximum recursion depth.
        visited: Set of visited types (to prevent cycles).
        
    Returns:
        Nested dictionary of type structure.
    """
    if visited is None:
        visited = set()
    
    if depth <= 0 or type_name in visited:
        return {"__ref": type_name}
    
    visited.add(type_name)
    type_def = find_type_by_name(schema, type_name)
    
    if type_def is None:
        return {"__unknown": type_name}
    
    result = {
        "kind": type_def.get("kind"),
        "name": type_name,
    }
    
    fields = type_def.get("fields", [])
    if fields:
        result["fields"] = {}
        for field in fields:
            field_type = _unwrap_type(field.get("type", {}))
            result["fields"][field.get("name")] = explore_type_tree(
                schema, field_type, depth - 1, visited.copy()
            )
    
    return result


def _unwrap_type(type_obj: dict[str, Any]) -> str:
    """Unwrap nested type references to get the base type name."""
    if type_obj.get("name"):
        return type_obj["name"]
    if type_obj.get("ofType"):
        return _unwrap_type(type_obj["ofType"])
    return "Unknown"


def generate_query_template(
    schema: dict[str, Any],
    query_field: str,
    depth: int = 3,
) -> str:
    """
    Generate a GraphQL query template for a query field.
    
    Args:
        schema: Schema introspection result.
        query_field: Name of the query field (e.g., "teams", "match").
        depth: Maximum field depth.
        
    Returns:
        GraphQL query string template.
    """
    query_fields = get_query_fields(schema)
    
    field_def = None
    for f in query_fields:
        if f.get("name") == query_field:
            field_def = f
            break
    
    if field_def is None:
        return f"# Query field '{query_field}' not found"
    
    # Get return type
    return_type = _unwrap_type(field_def.get("type", {}))
    
    # Generate args
    args = field_def.get("args", [])
    args_str = ""
    if args:
        arg_parts = []
        for arg in args:
            arg_name = arg.get("name")
            arg_type = _format_type(arg.get("type", {}))
            arg_parts.append(f"${arg_name}: {arg_type}")
        args_str = f"({', '.join(arg_parts)})"
    
    # Generate field selection
    type_def = find_type_by_name(schema, return_type)
    fields_str = _generate_field_selection(schema, type_def, depth)
    
    # Build query
    query_args = ""
    if args:
        arg_vals = [f"{a.get('name')}: ${a.get('name')}" for a in args]
        query_args = f"({', '.join(arg_vals)})"
    
    return f"""query {query_field.capitalize()}Query{args_str} {{
  {query_field}{query_args} {fields_str}
}}"""


def _format_type(type_obj: dict[str, Any]) -> str:
    """Format a type object as a GraphQL type string."""
    kind = type_obj.get("kind")
    name = type_obj.get("name")
    of_type = type_obj.get("ofType")
    
    if kind == "NON_NULL":
        return f"{_format_type(of_type)}!"
    elif kind == "LIST":
        return f"[{_format_type(of_type)}]"
    else:
        return name or "Unknown"


def _generate_field_selection(
    schema: dict[str, Any],
    type_def: Optional[dict[str, Any]],
    depth: int,
    indent: int = 2,
) -> str:
    """Generate field selection for a type."""
    if type_def is None or depth <= 0:
        return ""
    
    kind = type_def.get("kind")
    
    # Handle connection types
    if kind == "OBJECT" and type_def.get("name", "").endswith("Connection"):
        edges_type = None
        for f in type_def.get("fields", []):
            if f.get("name") == "edges":
                edges_type_name = _unwrap_type(f.get("type", {}))
                edges_type = find_type_by_name(schema, edges_type_name)
                break
        
        if edges_type:
            node_type = None
            for f in edges_type.get("fields", []):
                if f.get("name") == "node":
                    node_type_name = _unwrap_type(f.get("type", {}))
                    node_type = find_type_by_name(schema, node_type_name)
                    break
            
            if node_type:
                node_fields = _generate_field_selection(schema, node_type, depth - 1, indent + 2)
                return f"{{\n{'  ' * indent}edges {{\n{'  ' * (indent + 1)}node {node_fields}\n{'  ' * indent}}}\n{'  ' * (indent - 1)}}}"
    
    fields = type_def.get("fields", [])
    if not fields:
        return ""
    
    # Select scalar fields and first few object fields
    lines = ["{"]
    for field in fields[:10]:  # Limit fields
        field_name = field.get("name")
        field_type_name = _unwrap_type(field.get("type", {}))
        field_type = find_type_by_name(schema, field_type_name)
        
        if field_type is None:
            lines.append(f"{'  ' * indent}{field_name}")
        elif field_type.get("kind") in ("SCALAR", "ENUM"):
            lines.append(f"{'  ' * indent}{field_name}")
        elif depth > 1:
            nested = _generate_field_selection(schema, field_type, depth - 1, indent + 1)
            if nested:
                lines.append(f"{'  ' * indent}{field_name} {nested}")
    
    lines.append(f"{'  ' * (indent - 1)}}}")
    return "\n".join(lines)
