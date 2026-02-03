# VORACLE

**VALORANT Opponent Scouting Intelligence**

A professional scouting report generator for VALORANT esports teams, built for the Cloud9 x JetBrains Hackathon (Category 2: Automated Scouting Report Generator).

## Features

- **Full GRID Match Data**: Complete map scores, player stats (K/D/A, damage, headshots), and agent picks from official GRID API
- **Map Veto Analysis**: Real ban/pick sequences from competitive matches
- **Live Team Rankings**: Current rankings with W-L records from VLR.gg
- **Comprehensive Reports**: Map performance, player stats, economy analysis
- **AI-Powered Insights**: Pattern detection with counter-strategy recommendations
- **Beautiful UI**: VALORANT-inspired dark theme with Cloud9 cyan accents
- **Interactive Charts**: Win rate trends, map performance, player comparisons
- **PDF Export**: Print-ready scouting reports

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- GRID API Key (optional, falls back to VLR data)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/VORACLE.git
   cd VORACLE
   ```

2. **Install Python dependencies**
   ```bash
   pip install -e .
   ```

3. **Install frontend dependencies**
   ```bash
   cd apps/web
   npm install
   cd ../..
   ```

4. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your GRID API key
   ```

### Running the Application

1. **Start the API server**
   ```bash
   python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (in a new terminal)
   ```bash
   cd apps/web
   npm run dev
   ```

3. **Open your browser**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## Supported Teams

The application supports any VALORANT team. Popular teams with live data include:

**Americas (NA)**
- NRG, G2 Esports, Cloud9, Sentinels, 100 Thieves

**EMEA (EU)**
- Fnatic, Team Vitality, Team Liquid, Karmine Corp

**Pacific (APAC)**
- DRX, Paper Rex, T1, Gen.G

**LATAM**
- LOUD, Leviatan, KRU Esports

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | API health check |
| `GET /report?team=NAME&n=10` | Generate scouting report |
| `GET /report/debug?team=NAME` | Debug report with raw data |
| `GET /team/search?q=QUERY` | Search teams by name |
| `GET /team/popular?regions=na,eu` | Get popular teams with rankings |

## Project Structure

```
VORACLE/
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── main.py
│   │   └── routers/
│   └── web/              # Next.js frontend
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   └── lib/
│       └── package.json
├── packages/
│   └── core/             # Core business logic
│       ├── grid/         # GRID API client
│       ├── vlr/          # VLR.gg API client
│       ├── data/         # Combined data layer
│       ├── normalize/    # Data normalization
│       ├── metrics/      # Statistics computation
│       ├── insights/     # AI insight generation
│       └── report/       # Report builder
├── scripts/              # CLI tools
├── .env.example
└── README.md
```

## Data Sources

### GRID API (Primary)
- **File Download Endpoint**: Full match data including map scores, player stats
- **Central Data GraphQL**: Series listings, team info, tournament data
- Player statistics: Kills, Deaths, Assists, Damage, Headshots, First Kills
- Agent picks per map
- Map veto/ban sequences

### VLR.gg API (Supplementary)
- Live team rankings with W-L records
- Player aggregated statistics (Rating, ACS, K/D)
- Recent match results for broader coverage

## Data Quality

The application automatically assesses data quality and shows appropriate warnings:

- **Good**: Full match data and player statistics available
- **Rankings Only**: Win rate from VLR rankings, player stats available, but no individual match details
- **Partial**: Some data missing (e.g., players without detailed stats)
- **Mock Fallback**: Live data unavailable, showing demonstration data

Team name matching supports aliases:
- "Cloud9" / "C9"
- "100 Thieves" / "100T"
- "Sentinels" / "SEN"
- "Fnatic" / "FNC"
- And more...

## Tech Stack

**Backend**
- Python 3.9+
- FastAPI
- pandas
- httpx
- diskcache
- pydantic

**Frontend**
- Next.js 14
- TypeScript
- TailwindCSS
- Recharts
- Framer Motion

## Scripts

```bash
# Generate a report from CLI
python scripts/build_report.py --team "Cloud9"

# Test live data integration
python scripts/test_live_report.py

# Test multiple teams
python scripts/test_multiple_teams.py

# Fetch GRID schema
python scripts/fetch_schema.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GRID_API_KEY` | GRID API authentication key | No (uses VLR fallback) |
| `GRID_API_URL` | GRID API endpoint | No (has default) |
| `API_HOST` | API server host | No (default: 0.0.0.0) |
| `API_PORT` | API server port | No (default: 8000) |
| `CACHE_DIR` | Cache directory | No (default: .cache) |
| `CACHE_TTL` | Cache TTL in seconds | No (default: 3600) |

## Deployment

### Frontend (Vercel)

1. Push your code to GitHub
2. Import the repository in Vercel
3. Set the root directory to `apps/web`
4. Add environment variable: `NEXT_PUBLIC_API_URL` = your backend URL
5. Deploy

### Backend (Railway)

1. Push your code to GitHub
2. Create a new project in Railway
3. Add your repository
4. Set environment variables:
   - `GRID_API_KEY` = your GRID API key
   - `GRID_API_URL` = `https://api-op.grid.gg/central-data/graphql`
5. Deploy

The Procfile and railway.json are already configured for automatic deployment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Cloud9 and JetBrains for the hackathon
- GRID for the esports data API
- VLR.gg for live match data
- The VALORANT esports community
