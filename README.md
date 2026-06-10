# 🇳🇵 VANTAGE — AI-Powered News Intelligence & Media Bias Analysis Platform

> Understand how Nepal's media shapes political perception. Powered by LLM reasoning.

---

## Overview

VANTAGE is a full-stack AI platform that analyzes English-language Nepali news articles using LLM-driven reasoning. It detects bias at entity level, clusters multiple articles into events, and compares how different media houses frame the same political story.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        VANTAGE SYSTEM                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Ingestion   │  LLM Engine  │  Clustering  │   Frontend     │
│  (Scrapy)    │  (OpenAI /   │  (sentence-  │  (Next.js 14)  │
│              │   Ollama)    │  transformers)│                │
├──────────────┴──────────────┴──────────────┴────────────────┤
│               FastAPI Backend + PostgreSQL                    │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Scrapy + RSS feeds |
| Database | PostgreSQL + SQLAlchemy |
| ML/Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | OpenAI GPT-4o / Ollama (LLaMA 3 / Mistral) — switchable |
| Backend | FastAPI (async) + Celery + Redis |
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Charts | Recharts |
| Animations | Framer Motion |

## Quick Start

See `docs/SETUP.md` for full instructions.

```bash
# 1. Clone & setup env
cp .env.example .env

# 2. Start infrastructure
docker-compose up -d postgres redis

# 3. Backend
cd backend && pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 4. Scraper (separate terminal)
cd scraper && scrapy crawl kathmandu_post

# 5. Frontend
cd frontend && npm install && npm run dev
```

## Key Features

- **Event Clustering** — Groups articles from different publishers covering the same story
- **Entity-Level Bias (ABSA)** — "This article is critical of KP Oli, neutral towards RSP"
- **Media Report Cards** — Historical bias trends per publisher
- **AI Reasoning Panel** — LLM explains *why* an article is biased
- **Live Playground** — Paste any text, get instant LLM analysis
- **LLM Toggle** — Switch between OpenAI and Ollama with one click
