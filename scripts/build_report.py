#!/usr/bin/env python3
"""
VORACLE CLI Report Builder

Command-line tool for generating scouting reports locally.

Usage:
    python build_report.py --team "Cloud9"
    python build_report.py --team "Sentinels" --n 5 --mock
    python build_report.py --team "LOUD" --output report.json
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.core.report.build import build_report


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a VORACLE scouting report for a VALORANT team.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build_report.py --team "Cloud9"
    python build_report.py --team "Sentinels" --n 5 --mock
    python build_report.py --team "LOUD" --output report.json

Available mock teams: Cloud9, Sentinels, LOUD
        """,
    )
    
    parser.add_argument(
        "--team", "-t",
        type=str,
        required=True,
        help="Team name to generate report for",
    )
    
    parser.add_argument(
        "--n", "-n",
        type=int,
        default=10,
        help="Number of matches to analyze (default: 10)",
    )
    
    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="Use mock data instead of GRID API",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: print to stdout)",
    )
    
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON (no indentation)",
    )
    
    return parser.parse_args()


def print_report_summary(report: dict) -> None:
    """Print a human-readable summary of the report."""
    team = report.get("team_summary", {})
    
    print("\n" + "=" * 60)
    print(f"VORACLE SCOUTING REPORT: {team.get('name', 'Unknown')}")
    print("=" * 60)
    
    print(f"\n[TEAM OVERVIEW]")
    print(f"   Matches Analyzed: {team.get('matches_analyzed', 0)}")
    print(f"   Win Rate: {team.get('overall_win_rate', 0):.1%}")
    print(f"   Date Range: {team.get('date_range', 'N/A')}")
    
    # Trend Alerts
    trend_alerts = report.get("trend_alerts", [])
    if trend_alerts:
        print(f"\n[TREND ALERTS]")
        for alert in trend_alerts[:3]:
            direction = "^" if alert.get("direction") == "improving" else "v"
            print(f"   [{alert.get('significance', '?')}] {alert.get('metric', '')} {direction} {alert.get('change_pct', 0):.0f}%")
    
    # Map Veto
    map_veto = report.get("map_veto", [])
    if map_veto:
        print(f"\n[MAP VETO RECOMMENDATIONS]")
        for veto in map_veto[:5]:
            rec = veto.get("recommendation", "NEUTRAL")
            marker = {"BAN": "[X]", "PICK": "[+]", "NEUTRAL": "[ ]", "LOW_SAMPLE": "[?]"}.get(rec, "[ ]")
            print(f"   {marker} {veto.get('map_name', ''):12} {veto.get('win_rate', 0):.0%} ({veto.get('wins', 0)}/{veto.get('games', 0)})")
    
    # Map performance
    print(f"\n[MAP PERFORMANCE]")
    for map_stat in report.get("map_performance", []):
        wr = map_stat.get("win_rate", 0)
        bar = "#" * int(wr * 10) + "-" * (10 - int(wr * 10))
        print(f"   {map_stat.get('map_name', ''):12} [{bar}] {wr:.0%} ({map_stat.get('wins', 0)}/{map_stat.get('games', 0)})")
    
    # Side performance
    print(f"\n[SIDE PERFORMANCE]")
    for side_stat in report.get("side_performance", []):
        print(f"   {side_stat.get('side', '').capitalize():12} {side_stat.get('win_rate', 0):.1%} ({side_stat.get('rounds_won', 0)}/{side_stat.get('rounds_played', 0)})")
    
    # Economy
    if report.get("economy_stats"):
        eco = report["economy_stats"]
        print(f"\n[ECONOMY]")
        print(f"   Pistol Win Rate: {eco.get('pistol_win_rate', 0):.1%}")
        print(f"   Eco Conversion:  {eco.get('eco_conversion_rate', 0):.1%}")
    
    # Top players
    print(f"\n[TOP PLAYERS by ACS]")
    for i, player in enumerate(report.get("player_stats", [])[:5], 1):
        name = player.get('name', 'Unknown')[:12]
        acs = player.get('avg_acs', 0)
        agent = player.get('most_played_agent', 'Unknown')[:10]
        fb = player.get('first_blood_rate', 0)
        print(f"   {i}. {name:12} ACS: {acs:5.1f} | {agent:10} | FB: {fb:.1f}")
    
    # Key Insights
    print(f"\n[KEY INSIGHTS]")
    for insight in report.get("key_insights", [])[:5]:
        severity = insight.get("severity", "LOW")
        marker = {"HIGH": "[!]", "MED": "[*]", "LOW": "[-]"}.get(severity, "[?]")
        print(f"   {marker} {insight.get('title', '')}")
        print(f"       {insight.get('data_point', '')}")
    
    # How to beat them
    print(f"\n[HOW TO BEAT THEM]")
    for i, rec in enumerate(report.get("how_to_beat", [])[:6], 1):
        print(f"   {i}. {rec}")
    
    # What NOT to do
    what_not = report.get("what_not_to_do", [])
    if what_not:
        print(f"\n[WHAT NOT TO DO]")
        for i, warning in enumerate(what_not[:4], 1):
            print(f"   {i}. {warning}")
    
    print("\n" + "=" * 60)


async def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    print(f"Generating report for: {args.team}")
    print(f"Matches to analyze: {args.n}")
    print(f"Using mock data: {args.mock}")
    print()
    
    try:
        # Generate report
        report = await build_report(
            team_name=args.team,
            n_matches=args.n,
            use_mock=args.mock,
        )
        
        # Convert to dict for JSON serialization
        report_dict = report.model_dump()
        
        # Handle datetime serialization
        if "generated_at" in report_dict:
            report_dict["generated_at"] = report_dict["generated_at"].isoformat()
        
        # Output
        indent = None if args.compact else 2
        json_output = json.dumps(report_dict, indent=indent, default=str)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json_output)
            print(f"Report saved to: {output_path}")
            print_report_summary(report_dict)
        else:
            print_report_summary(report_dict)
            print("\n[FULL JSON REPORT]")
            print(json_output)
        
        return 0
        
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
