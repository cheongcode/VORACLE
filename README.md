# VORACLE - VALORANT Opponent Reconnaissance & Analysis for Competitive League Esports

<p align="center">
  <strong>AI-Powered Scouting Intelligence System for VALORANT</strong>
</p>

<p align="center">
  Built for the Cloud9 x JetBrains Hackathon | Category 2: Automated Scouting Report Generator
</p>

---

## Overview

VORACLE is a production-quality scouting report engine that transforms raw VALORANT match data into actionable competitive intelligence. Given a team name, it fetches their recent matches, analyzes strategic patterns, and generates coach-friendly reports with counter-strategy recommendations.

**This is NOT a dashboard. This is a REPORT ENGINE.**

### Key Features

- **Real GRID API Integration** - Fetch live match data from the official VALORANT esports data provider
- **Rule-Based Insight Engine** - 16 detection rules across 6 categories with evidence tracking
- **Comprehensive Metrics** - Win rates, loss patterns, player stats, trend analysis, meta comparison
- **Evidence-Backed Insights** - Every insight includes data evidence with sample rows
- **World-Class UI** - VALORANT dark theme with Cloud9 cyan accents
- **PDF Export** - Print-ready scouting reports

---

## Quick Start

### Prerequisites

- Python 3.9+ (Python 3.11+ recommended)
- Node.js 18+ (for frontend)
- GRID API key (optional, mock data available)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/VORACLE.git
cd VORACLE

# Install Python dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your GRID_API_KEY (optional)

# Install frontend dependencies
cd apps/web
npm install
```

### Running the Application

**Option 1: CLI (Quick Test)**

```bash
# Generate a report using mock data
py -3.9 scripts/build_report.py --team "Cloud9" --n 10 --mock

# Save to file
py -3.9 scripts/build_report.py --team "Sentinels" --output report.json
```

**Option 2: API Server**

```bash
# Start the FastAPI backend
py -3.9 -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

**Option 3: Full Stack**

```bash
# Terminal 1: Start backend
py -3.9 -m uvicorn apps.api.main:app --port 8000

# Terminal 2: Start frontend
cd apps/web
npm run dev

# Open http://localhost:3000 in your browser
```

---

## Architecture

```
VORACLE/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py             # Application entry point
│   │   └── routers/            # API endpoints
│   │       ├── report.py       # GET /report, GET /report/debug
│   │       └── team.py         # GET /team/search
│   └── web/                    # Next.js frontend
│       └── src/
│           ├── app/            # Pages (/, /report/[team])
│           ├── components/     # UI components
│           ├── lib/            # API client, utilities
│           ├── styles/         # Design tokens
│           └── types/          # TypeScript interfaces
├── packages/
│   └── core/                   # Core business logic
│       ├── grid/               # GRID API client
│       │   ├── client.py       # Async GraphQL client
│       │   ├── mock_data.py    # Mock data for testing
│       │   └── schema_introspect.py
│       ├── normalize/          # Data normalization
│       │   └── valorant.py     # Raw -> DataFrames
│       ├── metrics/            # Statistical metrics
│       │   └── valorant.py     # All metric computations
│       ├── insights/           # Rule-based insights
│       │   ├── rules.py        # 16 detection rules
│       │   └── generator.py    # Dedup, ranking, checklists
│       └── report/             # Report generation
│           ├── models.py       # Pydantic models
│           └── build.py        # Pipeline orchestration
└── scripts/
    ├── build_report.py         # CLI tool
    └── fetch_schema.py         # Schema introspection
```

### Data Pipeline

```
GRID API → Normalize → Metrics → Insights → Report JSON → UI → PDF
```

1. **GRID API** - Fetch raw match data via GraphQL
2. **Normalize** - Convert to clean pandas DataFrames
3. **Metrics** - Compute statistical metrics with evidence
4. **Insights** - Run rules, deduplicate, rank by impact
5. **Report** - Build structured JSON report
6. **UI** - Render interactive Next.js frontend
7. **PDF** - Export printable report

---

## API Reference

### GET /report

Generate a scouting report for a team.

**Parameters:**
- `team` (required): Team name to analyze
- `n` (default: 10): Number of matches to analyze
- `mock` (default: true): Use mock data instead of GRID API

**Response:**
```json
{
  "generated_at": "2026-01-29T12:00:00",
  "team_summary": {
    "name": "Cloud9",
    "matches_analyzed": 10,
    "overall_win_rate": 0.6,
    "date_range": "2025-12-01 to 2026-01-29"
  },
  "trend_alerts": [...],
  "map_veto": [...],
  "map_performance": [...],
  "side_performance": [...],
  "economy_stats": {...},
  "player_stats": [...],
  "capabilities": {...},
  "key_insights": [...],
  "how_to_beat": [...],
  "what_not_to_do": [...],
  "evidence_tables": {...}
}
```

### GET /report/debug

Debug endpoint with raw DataFrame information.

**Parameters:** Same as `/report`

**Response:**
```json
{
  "team_name": "Cloud9",
  "dataframes": [
    {
      "name": "matches_df",
      "shape": [10, 8],
      "columns": ["match_id", "date", "map", ...],
      "sample_rows": [...]
    }
  ],
  "metrics_summary": {...},
  "insight_summary": {...}
}
```

### GET /team/search

Search for teams by name.

**Parameters:**
- `q` (required): Search query (min 2 characters)
- `limit` (default: 10): Maximum results
- `use_mock` (default: false): Search mock data only

### GET /health

Health check endpoint.

---

## Insight System

VORACLE uses a rule-based insight engine with 16 rules across 6 categories:

### Rule Categories

| Category | Rules | Description |
|----------|-------|-------------|
| **Trend Alerts** | 3 | Win rate, pistol, and side balance shifts |
| **Loss Patterns** | 3 | Pistol collapse, early deficit, eco vulnerability |
| **Agent Neutralization** | 3 | Agent dependency, targeting, entry reliance |
| **Map Veto** | 3 | Maps to ban, pick, or watch |
| **Playbook Predictor** | 2 | Pistol tendencies, side preferences |
| **Meta Comparison** | 2 | Above/below baseline performance |

### Insight Structure

Each insight includes:

```json
{
  "title": "Pistol Loss Collapse",
  "severity": "HIGH",
  "confidence": "high",
  "data_point": "Lose 78% of matches after losing first pistol (n=9)",
  "interpretation": "Team struggles to recover from pistol losses...",
  "recommendation": "Prioritize winning pistol rounds...",
  "what_not_to_do": "Don't force after winning pistol...",
  "evidence_refs": [
    {
      "table": "matches_df",
      "filters": {"lost_pistol": true},
      "sample_rows": [...]
    }
  ],
  "impact_score": 0.72
}
```

### Impact Scoring

Insights are ranked by:

```
impact_score = confidence_weight × effect_size × frequency_factor
```

- **confidence_weight**: 1.0 (high), 0.7 (medium), 0.4 (low)
- **effect_size**: Magnitude of the finding (e.g., 78% vs 50%)
- **frequency_factor**: log(sample_size) normalized

---

## Report Sections

The scouting report includes:

1. **Team Summary** - Overview with win rate, matches analyzed, date range
2. **Trend Alerts** - Significant changes in last 3 vs last 10 matches
3. **Map Veto Recommendations** - BAN/PICK/NEUTRAL with confidence
4. **Map Performance** - Win rate per map with visual bars
5. **Side Performance** - Attack vs Defense round win rates
6. **Economy Stats** - Pistol and eco round performance
7. **Player Stats** - Per-player ACS, agents, K/D, FB rate
8. **Capabilities** - Radar chart of team strengths
9. **Key Insights** - Top 6-12 insights with evidence drawers
10. **How to Beat Them** - Actionable checklist
11. **What NOT to Do** - Warnings and anti-patterns
12. **Evidence Appendix** - Raw data tables for verification

---

## Design System

### Theme

- **Background**: VALORANT Dark (#0F1923)
- **Cards**: Elevated surface (#1F2D3D)
- **Accent**: Cloud9 Cyan (#00AEEF)
- **Alert**: VALORANT Red (#FF4655)
- **Typography**: Inter (headers), JetBrains Mono (data)

### Components

- `Card` - Base container with glass morphism
- `StatPill` - Compact stat display
- `ConfidenceBadge` - HIGH/MED/LOW indicator
- `SeverityBadge` - Alert level indicator
- `InsightCard` - Expandable with evidence drawer
- `ChecklistBlock` - Printable with checkboxes
- `TrendAlertStrip` - Horizontal trend indicator
- `MapVetoCard` - BAN/PICK recommendation card

---

## Configuration

### Environment Variables

```bash
# .env file

# GRID API (optional - mock data available)
GRID_API_KEY=your_api_key_here
GRID_API_URL=https://api.grid.gg/central-data/graphql

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Caching
CACHE_DIR=.cache
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO

# Report Configuration
MAX_INSIGHTS=12
MIN_INSIGHTS=6
```

### Mock Teams

For testing without GRID API access:
- Cloud9
- Sentinels
- LOUD

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_normalize.py -v

# Run with coverage
pytest --cov=packages/core
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format with ruff
ruff format .

# Type checking
mypy packages/
```

### Project Standards

- **Python**: Type hints, docstrings, defensive parsing
- **TypeScript**: Strict mode, interface definitions
- **Components**: Framer Motion animations, responsive design
- **API**: Pydantic validation, structured error handling

---

## Tech Stack

### Backend
- **Python 3.9+** - Core language
- **FastAPI** - Web framework
- **pandas** - Data manipulation
- **httpx** - Async HTTP client
- **pydantic** - Data validation
- **diskcache** - Response caching

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first CSS
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **lucide-react** - Icons

---

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'diskcache'"**
```bash
# Ensure you're using the correct Python version
py -3.9 -m pip install -e .
```

**"Port already in use"**
```bash
# Kill existing process or use different port
py -3.9 -m uvicorn apps.api.main:app --port 8001
```

**"GRID API error"**
- Check your API key is set correctly in `.env`
- Use `mock=true` to test with mock data

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **Cloud9** - Hackathon sponsor and design inspiration
- **JetBrains** - Development tools and hackathon support
- **GRID** - Official VALORANT esports data provider
- **Riot Games** - VALORANT game and esports ecosystem

---

<p align="center">
  Built with precision for competitive excellence.
</p>
