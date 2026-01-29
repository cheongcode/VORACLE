#!/usr/bin/env python3
"""
GRID Schema Fetcher

Fetches the GRID GraphQL schema via introspection and saves it to a JSON file.

Usage:
    python fetch_schema.py
    python fetch_schema.py --output custom/path/schema.json
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.core.grid.client import GRIDClient
from packages.core.grid.schema_introspect import (
    save_schema,
    get_query_fields,
    get_type_names,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch GRID GraphQL schema via introspection.",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="packages/core/grid/schema/schema.json",
        help="Output path for schema JSON file",
    )
    
    parser.add_argument(
        "--explore",
        action="store_true",
        help="Print schema exploration summary",
    )
    
    return parser.parse_args()


async def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    print("Fetching GRID GraphQL schema...")
    print()
    
    try:
        async with GRIDClient() as client:
            schema = await client.introspect()
            
            # Save schema
            output_path = Path(args.output)
            save_schema(schema, output_path)
            print(f"Schema saved to: {output_path}")
            
            # Print summary
            if args.explore:
                print()
                print("=" * 60)
                print("SCHEMA SUMMARY")
                print("=" * 60)
                
                # Query fields
                query_fields = get_query_fields(schema)
                print(f"\nQuery Fields ({len(query_fields)}):")
                for field in query_fields[:20]:
                    print(f"  - {field.get('name')}")
                if len(query_fields) > 20:
                    print(f"  ... and {len(query_fields) - 20} more")
                
                # Object types
                object_types = get_type_names(schema, "OBJECT")
                object_types = [t for t in object_types if not t.startswith("__")]
                print(f"\nObject Types ({len(object_types)}):")
                for t in object_types[:30]:
                    print(f"  - {t}")
                if len(object_types) > 30:
                    print(f"  ... and {len(object_types) - 30} more")
                
                # Input types
                input_types = get_type_names(schema, "INPUT_OBJECT")
                print(f"\nInput Types ({len(input_types)}):")
                for t in input_types[:15]:
                    print(f"  - {t}")
                if len(input_types) > 15:
                    print(f"  ... and {len(input_types) - 15} more")
                
                print()
                print("=" * 60)
            
            return 0
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
