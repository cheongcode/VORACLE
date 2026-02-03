#!/usr/bin/env python3
"""Test live report generation."""
import asyncio
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.report.build import build_report


async def test():
    try:
        print("Building report for Sentinels...")
        report = await build_report('Sentinels', n_matches=10, use_mock=False)
        
        print("SUCCESS!")
        print(f"Team: {report.team_summary.name}")
        print(f"Matches: {report.team_summary.matches_analyzed}")
        print(f"Win Rate: {report.team_summary.overall_win_rate * 100:.1f}%")
        print(f"Data Source: {report.meta.get('data_source')}")
        print(f"Insights: {len(report.key_insights)}")
        
        if report.meta.get('team_info'):
            info = report.meta['team_info']
            print(f"\nTeam Info from API:")
            print(f"  Rank: {info.get('rank')}")
            print(f"  Record: {info.get('record')}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
