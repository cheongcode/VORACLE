# VORACLE: VALORANT Opponent Reconnaissance & Competitive Intelligence Engine

## Executive Summary

VORACLE is an automated scouting report generator that transforms raw esports data into actionable competitive intelligence for VALORANT teams. Built for the Cloud9 x JetBrains Hackathon, VORACLE addresses a critical gap in the competitive VALORANT ecosystem: the time-intensive nature of opponent analysis.

Professional VALORANT teams typically spend 10-20 hours per week manually reviewing VODs, compiling statistics, and creating scouting reports. VORACLE automates this entire workflow, delivering comprehensive opponent analysis in under 30 seconds.

---

## The Problem

### Current State of VALORANT Scouting

1. **Time-Intensive Manual Process**
   - Analysts watch hours of VODs for each opponent
   - Statistics are manually compiled in spreadsheets
   - Reports take 4-8 hours to create per opponent

2. **Data Fragmentation**
   - Match data scattered across multiple platforms (VLR, Liquipedia, GRID)
   - No unified view of opponent tendencies
   - Historical data difficult to aggregate

3. **Inconsistent Analysis Quality**
   - Human bias in pattern recognition
   - Missed statistical anomalies
   - Subjective interpretation of tendencies

4. **Accessibility Gap**
   - Only top-tier organizations can afford dedicated analysts
   - Tier 2/3 teams lack competitive intelligence resources
   - Amateur teams have zero scouting infrastructure

---

## The Solution: VORACLE

VORACLE is a full-stack scouting intelligence platform that:

1. **Aggregates** data from official (GRID) and community (VLR.gg) sources
2. **Normalizes** disparate data formats into unified analytics
3. **Analyzes** patterns using statistical and rule-based engines
4. **Generates** actionable insights with confidence scoring
5. **Presents** information in a beautiful, VALORANT-themed interface

### How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GRID API   │────▶│  Data Layer │────▶│   Metrics   │
│  VLR.gg API │     │  (Combined) │     │   Engine    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Report    │◀────│   Insight   │◀────│    Rules    │
│   Builder   │     │  Generator  │     │   Engine    │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│  Next.js UI │
│  PDF Export │
└─────────────┘
```

---

## Features

### 1. Real-Time Data Integration

**GRID API Integration**
- Official tournament data with 100% accuracy
- Complete match data via file-download endpoint
- Map scores, player stats, agent picks
- Map veto sequences (bans and picks)

**VLR.gg Integration**
- Live team rankings with W-L records
- Player aggregated statistics (Rating, ACS, K/D)
- Broader match coverage for context

### 2. Comprehensive Match Analysis

| Metric | Description |
|--------|-------------|
| **Map Performance** | Win rates per map with round differentials |
| **Side Performance** | Attack vs Defense round win percentages |
| **Economy Analysis** | Pistol round win rates, eco conversion |
| **Player Statistics** | K/D/A, ACS, first bloods, headshot % |
| **Agent Pool Analysis** | Agent picks per player with win rates |
| **Map Veto Patterns** | Historical ban/pick tendencies |

### 3. AI-Powered Insights

The insight engine generates actionable intelligence:

- **Trend Alerts**: Detecting performance shifts (last 3 vs last 10 matches)
- **Loss Patterns**: Identifying conditions that lead to losses
- **Map Recommendations**: Data-driven veto suggestions
- **Player Threats**: Highlighting dangerous players to neutralize
- **Counter-Strategies**: Specific recommendations to exploit weaknesses

Example Insight:
```
HIGH SEVERITY | HIGH CONFIDENCE
"Team loses 73% of rounds after losing pistol (n=22)"

Recommendation: Invest heavily in anti-eco rounds after winning pistol.
Force buy if you lose pistol to contest their eco momentum.
```

### 4. Beautiful VALORANT-Themed UI

- Dark theme matching VALORANT's aesthetic (#0F1923)
- Cloud9 cyan accent colors (#00AEEF)
- Animated components with Framer Motion
- Interactive charts (Recharts)
- Responsive design for all devices
- Print-ready PDF export

### 5. Team Search & Discovery

- Live team rankings from VLR.gg
- Region filtering (NA, EU, APAC, LATAM)
- Alias support (Cloud9 ↔ C9, Sentinels ↔ SEN)
- Popular teams quick-select

---

## Technical Architecture

### Backend (Python/FastAPI)

```
packages/core/
├── grid/           # GRID API client with caching
│   ├── client.py   # GraphQL client with retry logic
│   └── valorant.py # VALORANT-specific data fetching
├── vlr/            # VLR.gg API client
│   └── client.py   # REST client for rankings/stats
├── data/           # Combined data layer
│   └── combined.py # Multi-source data aggregation
├── normalize/      # Data normalization
│   └── valorant.py # Schema standardization
├── metrics/        # Statistical computation
│   └── valorant.py # Win rates, performance metrics
├── insights/       # Intelligence generation
│   ├── rules.py    # Rule-based pattern detection
│   └── generator.py # Insight ranking and deduplication
└── report/         # Report assembly
    ├── models.py   # Pydantic data models
    └── build.py    # Report orchestration
```

### Frontend (Next.js/TypeScript)

```
apps/web/src/
├── app/
│   ├── page.tsx           # Landing page with team search
│   └── report/[team]/     # Dynamic report pages
├── components/
│   ├── charts/            # Recharts visualizations
│   ├── report/            # Report section components
│   ├── search/            # Team search interface
│   └── ui/                # Reusable UI components
├── hooks/
│   └── useReport.ts       # Data fetching hook
├── lib/
│   └── api.ts             # API client
└── styles/
    └── tokens.ts          # Design system tokens
```

### Key Technical Decisions

1. **Async Python**: All API calls are async for performance
2. **Disk Caching**: Responses cached with TTL to reduce API load
3. **Defensive Parsing**: Graceful handling of missing/malformed data
4. **Type Safety**: Full Pydantic models and TypeScript types
5. **Modular Design**: Each component independently testable

---

## Feasibility Analysis

### Technical Feasibility: HIGH

| Factor | Assessment |
|--------|------------|
| **Data Availability** | GRID provides comprehensive match data; VLR supplements with rankings |
| **API Reliability** | Both APIs are stable with good documentation |
| **Processing Speed** | Report generation completes in <30 seconds |
| **Scalability** | Stateless architecture scales horizontally |
| **Deployment** | Standard cloud deployment (Vercel + Railway) |

### Market Feasibility: HIGH

| Factor | Assessment |
|--------|------------|
| **Target Market** | 500+ professional/semi-pro VALORANT teams globally |
| **Pain Point** | Validated - teams spend 10-20 hrs/week on scouting |
| **Competitive Landscape** | No direct competitors with this automation level |
| **Adoption Barrier** | Low - web-based, no installation required |

### Financial Feasibility: HIGH

| Cost Component | Estimate |
|----------------|----------|
| **Hosting (Railway)** | $5-20/month |
| **Hosting (Vercel)** | Free tier sufficient |
| **GRID API** | Free for basic access |
| **Development** | One-time (hackathon) |

---

## Value Proposition

### For Professional Teams

1. **Time Savings**: 10-20 hours/week → 30 seconds
2. **Consistency**: Same analytical rigor for every opponent
3. **Data-Driven**: Remove human bias from analysis
4. **Completeness**: Never miss a pattern or trend

### For Tier 2/3 Teams

1. **Accessibility**: Enterprise-level analytics without enterprise budget
2. **Competitive Edge**: Level the playing field against better-resourced opponents
3. **Professionalization**: Structured approach to opponent analysis

### For Content Creators & Analysts

1. **Research Tool**: Quickly gather statistics for content
2. **Narrative Discovery**: Find interesting storylines in data
3. **Verification**: Fact-check assumptions with real data

### For Tournament Organizers

1. **Broadcast Enhancement**: Real-time team comparisons
2. **Storyline Generation**: Data-backed narratives for casting
3. **Viewer Engagement**: Shareable scouting reports

---

## Competitive Analysis

| Solution | Pros | Cons |
|----------|------|------|
| **Manual Scouting** | Deep qualitative insights | Time-intensive, inconsistent |
| **Generic Stats Sites** | Quick access to numbers | No actionable insights |
| **Private Analytics Teams** | Customized analysis | Expensive, only for top teams |
| **VORACLE** | Automated, actionable, accessible | Limited by API data availability |

### VORACLE's Unique Position

VORACLE is the only solution that:
- Automates the entire scouting workflow
- Generates actionable recommendations (not just statistics)
- Is accessible to teams at all levels
- Provides professional-quality UI/UX

---

## Future Roadmap

### Phase 1: Foundation (Current)
- [x] GRID API integration
- [x] VLR.gg integration
- [x] Basic metrics computation
- [x] Rule-based insights
- [x] Web interface
- [x] PDF export

### Phase 2: Enhanced Intelligence
- [ ] AI-powered narrative summaries (Gemini integration)
- [ ] Match prediction model
- [ ] Player threat scoring
- [ ] Historical trend analysis
- [ ] Custom report templates

### Phase 3: Team Features
- [ ] User accounts and saved reports
- [ ] Team comparison tool
- [ ] Tournament bracket analysis
- [ ] Watchlist and alerts
- [ ] API access for integrations

### Phase 4: Platform Expansion
- [ ] Mobile app
- [ ] Discord bot integration
- [ ] Live match tracking
- [ ] Post-match analysis automation
- [ ] Coach collaboration tools

---

## Success Metrics

### Technical KPIs
- Report generation time: <30 seconds
- API uptime: >99%
- Data freshness: <1 hour delay
- Error rate: <1%

### User KPIs
- Reports generated per day
- Unique teams analyzed
- Return user rate
- Time saved per report (estimated)

### Business KPIs
- Active teams using platform
- Premium feature adoption
- API integration partners
- Tournament organizer partnerships

---

## Conclusion

VORACLE represents a significant advancement in VALORANT competitive intelligence. By automating the scouting process and generating actionable insights, it democratizes access to professional-level opponent analysis.

The project is:
- **Technically Sound**: Built on proven technologies with robust architecture
- **Market Ready**: Addresses validated pain points with clear value proposition
- **Financially Viable**: Low operating costs with multiple monetization paths
- **Scalable**: Architecture supports growth from hackathon demo to production platform

For the Cloud9 x JetBrains Hackathon, VORACLE demonstrates:
1. Deep integration with GRID's data ecosystem
2. Creative application of esports data
3. Professional-quality user experience
4. Clear path to real-world impact

---

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/cheongcode/VORACLE.git
cd VORACLE

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd apps/web && npm install && cd ../..

# Configure environment
cp .env.example .env
# Edit .env with your GRID_API_KEY

# Start backend
python -m uvicorn apps.api.main:app --port 8000

# Start frontend (new terminal)
cd apps/web && npm run dev
```

### Production Deployment

**Backend (Railway)**
1. Connect GitHub repo
2. Add environment variables: `GRID_API_KEY`, `GRID_API_URL`
3. Deploy

**Frontend (Vercel)**
1. Import from GitHub
2. Set root directory: `apps/web`
3. Add `NEXT_PUBLIC_API_URL` pointing to Railway
4. Deploy

---

## Team

Built for the **Cloud9 x JetBrains Hackathon** - Category 2: Automated Scouting Report Generator

---

## License

MIT License - Open source for the VALORANT community.

---

*VORACLE: Know your enemy. Win your match.*
