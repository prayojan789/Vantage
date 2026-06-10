# VANTAGE — Full Setup Guide

> From zero to running platform in ~10 minutes.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.10+ | python.org |
| Node.js | 18+ | nodejs.org |
| Docker + Compose | Latest | docker.com |
| Git | Any | git-scm.com |
| Ollama (optional) | Latest | ollama.ai |

---

## Step 1 — Clone & Configure Environment

```bash
git clone <your-repo-url> vantage
cd vantage

# Copy env template
cp .env.example .env
```

Open `.env` and set at minimum:

```env
# Required if using OpenAI
OPENAI_API_KEY=sk-your-key-here

# Or switch to Ollama (free, local)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
```

---

## Step 2 — Start Infrastructure (PostgreSQL + Redis)

```bash
docker-compose up -d
```

Verify both containers are healthy:

```bash
docker-compose ps
# postgres → healthy
# redis   → running
```

---

## Step 3 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (creates all tables)
alembic upgrade head
```

---

## Step 4 — Seed the Database

```bash
cd ..

# Seed media sources only
python scripts/seed_db.py

# OR seed media sources + demo articles (recommended for first run)
python scripts/seed_db.py --demo
```

The `--demo` flag inserts one pre-analyzed event cluster with 3 articles from different sources, complete with LLM outputs. This lets you explore the dashboard immediately without waiting for the scraper.

---

## Step 5 — Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify at: http://localhost:8000/health
API docs: http://localhost:8000/api/docs

---

## Step 6 — Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: **http://localhost:3000**

---

## Step 7 — Start Celery Workers (Background Processing)

Open two additional terminals:

**Terminal A — Worker (processes LLM analysis tasks):**
```bash
cd backend
source .venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
```

**Terminal B — Beat Scheduler (triggers tasks on schedule):**
```bash
cd backend
source .venv/bin/activate
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## Step 8 — Run the Scrapers

Each spider runs independently. Open a new terminal per spider:

```bash
cd scraper
source ../backend/.venv/bin/activate

# Kathmandu Post
scrapy crawl kathmandu_post

# Republica
scrapy crawl republica

# OnlineKhabar
scrapy crawl online_khabar
```

After scraping, the Celery worker will automatically pick up new articles and run LLM analysis + clustering.

---

## Step 9 (Optional) — Ollama Local LLM

If you want to run everything locally without an OpenAI key:

```bash
# Install Ollama from https://ollama.ai

# Pull the model (one-time, ~4GB)
ollama pull llama3

# Start Ollama server
ollama serve
```

Then in `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

You can also switch providers live from the dashboard UI without restarting anything.

---

## Demo Flow (For Project Defence)

1. **Start all services** (Steps 5 + 6)
2. **Open** http://localhost:3000 → Overview page shows live stats
3. **Dashboard** → Event Clusters page shows the pre-seeded event cluster with 3 articles
4. **Click an event** → Right panel shows AI reasoning (entities, bias score, framing analysis)
5. **Playground** → Paste any paragraph from a real news article → click Run Analysis → live LLM output in ~2 seconds
6. **Analytics** → Bias distribution chart, entity sentiment rankings, source report cards
7. **Toggle LLM** → Switch between OpenAI ↔ Ollama from the sidebar widget

---

## Architecture Summary

```
┌──────────────────────────────────────────────────────────────────┐
│  Scrapy Spiders (Kathmandu Post, Republica, OnlineKhabar)        │
│  RSS → Article HTML → PostgreSQL (raw articles)                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │ new article inserted
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Celery Worker                                                    │
│  1. sentence-transformers → article embedding                    │
│  2. Cosine similarity → assign to existing Event or create new   │
│  3. LLM (OpenAI / Ollama) → structured JSON analysis            │
│     ├─ Entity extraction (PERSON, ORG, PARTY, LOCATION)          │
│     ├─ Sentiment per entity (-1.0 to +1.0)                       │
│     ├─ Framing (critical / supportive / neutral / mixed)         │
│     ├─ Bias score (0.0 to 1.0)                                   │
│     └─ Framing explanation + bias reasoning                       │
└────────────────────────┬─────────────────────────────────────────┘
                         │ results stored in PostgreSQL
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  FastAPI Backend (port 8000)                                      │
│  REST endpoints: /api/events, /api/articles, /api/analytics,     │
│  /api/playground/analyze, /api/llm/provider                      │
└────────────────────────┬─────────────────────────────────────────┘
                         │ JSON
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Next.js Frontend (port 3000)                                     │
│  Overview · Event Clusters · Media Sources · Analytics ·         │
│  AI Playground                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Project Folder Structure

```
vantage/
├── .env.example               # Environment variables template
├── docker-compose.yml         # PostgreSQL + Redis
├── README.md
│
├── backend/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial.py
│   └── app/
│       ├── main.py            # FastAPI entry point
│       ├── tasks.py           # Celery tasks
│       ├── core/
│       │   └── config.py      # Settings (pydantic-settings)
│       ├── db/
│       │   └── database.py    # Async SQLAlchemy engine
│       ├── models/
│       │   └── models.py      # ORM models
│       ├── schemas/
│       │   └── schemas.py     # Pydantic schemas
│       ├── api/routes/
│       │   └── routes.py      # All REST endpoints
│       └── services/
│           ├── llm/
│           │   ├── provider.py  # OpenAI + Ollama router
│           │   ├── prompts.py   # Prompt engineering
│           │   └── analyzer.py  # Article analysis orchestrator
│           └── clustering/
│               └── clusterer.py # Embedding + event clustering
│
├── scraper/
│   ├── scrapy.cfg
│   ├── settings.py
│   ├── spiders/
│   │   └── news_spiders.py    # KP, Republica, OnlineKhabar spiders
│   └── pipelines/
│       └── db_pipeline.py     # Duplicate filter + PostgreSQL saver
│
├── frontend/
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── app/
│       │   ├── page.tsx           # Overview / Landing
│       │   ├── dashboard/page.tsx # Event Clusters
│       │   ├── analytics/page.tsx # Charts + Report Cards
│       │   ├── sources/page.tsx   # Media Sources
│       │   └── playground/page.tsx# AI Playground
│       ├── components/
│       │   ├── layout/Sidebar.tsx
│       │   ├── analysis/
│       │   │   ├── EventCard.tsx
│       │   │   ├── AIInsightPanel.tsx
│       │   │   └── DashboardStats.tsx
│       │   ├── charts/BiasCharts.tsx
│       │   └── ui/
│       │       ├── BiasScoreBar.tsx
│       │       ├── EntityPill.tsx
│       │       └── LLMProviderToggle.tsx
│       ├── lib/
│       │   ├── api.ts
│       │   └── utils.ts
│       └── types/index.ts
│
└── scripts/
    └── seed_db.py             # DB seeder + demo data
```

---

## Common Issues

**`alembic upgrade head` fails with "connection refused"**
→ Make sure `docker-compose up -d` ran successfully and postgres is healthy.

**OpenAI 401 error**
→ Check your `OPENAI_API_KEY` in `.env`. Key must start with `sk-`.

**Ollama "connection refused"**
→ Run `ollama serve` in a separate terminal before starting the backend.

**Scrapy yields nothing**
→ The news portals may have changed their HTML structure. Check the spider CSS selectors in `scraper/spiders/news_spiders.py` and update as needed.

**Frontend shows empty dashboard**
→ Run `python scripts/seed_db.py --demo` to insert demo data, then reload.
