#!/usr/bin/env python3
"""Test live report generation with multiple teams."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.report.build import build_report


async def test_team(team_name):
    try:
        report = await build_report(team_name, n_matches=10, use_mock=False)
        
        print(f"\n{'='*50}")
        print(f"Team: {report.team_summary.name}")
        print(f"Matches: {report.team_summary.matches_analyzed}")
        print(f"Win Rate: {report.team_summary.overall_win_rate * 100:.1f}%")
        print(f"Data Source: {report.meta.get('data_source')}")
        
        if report.meta.get('team_info'):
            info = report.meta['team_info']
            print(f"Rank: {info.get('rank')}, Record: {info.get('record')}")
        
        print(f"Insights: {len(report.key_insights)}")
        print(f"Maps: {[m.map_name for m in report.map_performance[:3]]}")
        
        return True
        
    except Exception as e:
        print(f"\n{team_name}: ERROR - {e}")
        return False


async def main():
    teams = ["Sentinels", "Cloud9", "NRG", "G2 Esports", "LOUD", "Fnatic"]
    
    print("Testing live report generation with multiple teams...")
    
    for team in teams:
        await test_team(team)


if __name__ == "__main__":
    asyncio.run(main())
