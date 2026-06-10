"""
VANTAGE — Database Seed Script
Run once after `alembic upgrade head` to populate media sources
and optionally insert demo articles for development.

Usage:
    cd backend
    python ../scripts/seed_db.py
    python ../scripts/seed_db.py --demo   # also inserts demo articles + LLM outputs
"""
import sys
import uuid
import json
import argparse
from datetime import datetime, timedelta
import random
import psycopg2
from psycopg2.extras import execute_values

# Read DB URL from env or use default
import os
DB_URL = os.getenv(
    "DATABASE_URL_SYNC",
    "postgresql://vantage:vantage_pass@localhost:5432/vantage_db"
)

MEDIA_SOURCES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Kathmandu Post",
        "slug": "kathmandu-post",
        "base_url": "https://kathmandupost.com",
        "rss_feed_url": "https://kathmandupost.com/rss",
        "logo_url": None,
        "is_active": True,
        "avg_bias_score": 0.0,
        "total_articles": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Republica",
        "slug": "republica",
        "base_url": "https://myrepublica.nagariknetwork.com",
        "rss_feed_url": "https://myrepublica.nagariknetwork.com/rss",
        "logo_url": None,
        "is_active": True,
        "avg_bias_score": 0.0,
        "total_articles": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "OnlineKhabar English",
        "slug": "online-khabar",
        "base_url": "https://english.onlinekhabar.com",
        "rss_feed_url": "https://english.onlinekhabar.com/feed",
        "logo_url": None,
        "is_active": True,
        "avg_bias_score": 0.0,
        "total_articles": 0,
    },
]

# Demo articles — one event cluster with 3 articles from different sources
DEMO_EVENT = {
    "id": str(uuid.uuid4()),
    "title": "Parliament passes controversial Education Reform Bill amid opposition walkout",
    "summary": "The House of Representatives passed the Education Reform Bill by a simple majority after the main opposition parties staged a walkout, citing inadequate stakeholder consultation.",
    "bias_divergence_score": 0.41,
    "article_count": 3,
    "centroid_embedding": None,
}

DEMO_ARTICLES = [
    {
        "title": "Govt pushes through Education Bill despite opposition protests",
        "content": "The ruling coalition rammed through the controversial Education Reform Bill on Tuesday, ignoring fierce criticism from opposition parties. Prime Minister KP Sharma Oli defended the legislation as transformative, while RSP leader Rabi Lamichhane called it an attack on institutional autonomy. The bill passed with 162 votes in favor.",
        "source_slug": "kathmandu-post",
        "bias_score": 0.71,
        "framing": "critical",
        "author": "Staff Reporter",
    },
    {
        "title": "Parliament approves Education Reform Bill; PM calls it historic step",
        "content": "Parliament on Tuesday approved the much-anticipated Education Reform Bill, with Prime Minister KP Sharma Oli hailing it as a landmark achievement for the country's future. The bill, which introduces sweeping changes to university governance, was passed by a comfortable majority. Opposition parties boycotted the vote, a move critics called irresponsible.",
        "source_slug": "republica",
        "bias_score": 0.38,
        "framing": "supportive",
        "author": "Parliamentary Correspondent",
    },
    {
        "title": "Education Bill passed amid controversy; experts divided",
        "content": "The Education Reform Bill cleared parliament on Tuesday with 162 votes in favor and 87 against, after opposition parties walked out of the session. Education experts remain divided on the bill's merit. RSP's Rabi Lamichhane and NC's Sher Bahadur Deuba both issued statements criticizing the process, while UML members celebrated the outcome.",
        "source_slug": "online-khabar",
        "bias_score": 0.29,
        "framing": "neutral",
        "author": "News Desk",
    },
]

DEMO_LLM_OUTPUTS = [
    {
        "framing_analysis": "The article uses charged language ('rammed through', 'ignoring fierce criticism') that frames the government's actions as aggressive and dismissive. The opposition perspective is given more sympathetic framing.",
        "bias_reasoning": "Words like 'rammed through' and 'controversial' signal editorial disapproval. The article leads with opposition criticism rather than the bill's content, shaping reader perception before facts are presented.",
        "event_summary": "Nepal's parliament passed the Education Reform Bill by a simple majority. Opposition parties walked out before the vote.",
        "entities": [
            {"name": "KP Sharma Oli", "type": "PERSON", "sentiment": "negative", "sentiment_score": -0.55, "framing": "critical", "context_snippet": "ruling coalition rammed through...ignoring fierce criticism"},
            {"name": "Rabi Lamichhane", "type": "PERSON", "sentiment": "positive", "sentiment_score": 0.3, "framing": "supportive", "context_snippet": "called it an attack on institutional autonomy"},
            {"name": "RSP", "type": "PARTY", "sentiment": "positive", "sentiment_score": 0.25, "framing": "supportive", "context_snippet": "RSP leader raised institutional concerns"},
        ],
    },
    {
        "framing_analysis": "The article adopts a largely pro-government framing, leading with the PM's celebratory quote and characterizing the opposition walkout as 'irresponsible'. Policy details are presented favorably.",
        "bias_reasoning": "'Much-anticipated' and 'landmark achievement' are editorial endorsements embedded in news reporting. Describing the opposition boycott as 'irresponsible' without attribution reveals editorial stance.",
        "event_summary": "Nepal's parliament approved the Education Reform Bill. PM Oli called it historic; opposition parties boycotted the vote.",
        "entities": [
            {"name": "KP Sharma Oli", "type": "PERSON", "sentiment": "positive", "sentiment_score": 0.72, "framing": "supportive", "context_snippet": "hailing it as a landmark achievement"},
            {"name": "Rabi Lamichhane", "type": "PERSON", "sentiment": "negative", "sentiment_score": -0.35, "framing": "critical", "context_snippet": "boycott called irresponsible by critics"},
        ],
    },
    {
        "framing_analysis": "The article maintains largely neutral framing, leading with vote tallies and attributing all opinions explicitly. Both government and opposition voices are given comparable space.",
        "bias_reasoning": "Bias score is low because the article leads with factual vote count, uses attribution ('experts remain divided'), and quotes both sides proportionally. Minor bias from sequencing opposition quotes last.",
        "event_summary": "The Education Reform Bill passed Nepal's parliament 162-87. Opposition parties walked out. Expert opinion is divided on the bill's merits.",
        "entities": [
            {"name": "KP Sharma Oli", "type": "PERSON", "sentiment": "neutral", "sentiment_score": 0.05, "framing": "neutral", "context_snippet": "UML members celebrated the outcome"},
            {"name": "Rabi Lamichhane", "type": "PERSON", "sentiment": "neutral", "sentiment_score": -0.1, "framing": "neutral", "context_snippet": "issued statements criticizing the process"},
            {"name": "Sher Bahadur Deuba", "type": "PERSON", "sentiment": "neutral", "sentiment_score": -0.1, "framing": "neutral", "context_snippet": "issued statements criticizing the process"},
            {"name": "RSP", "type": "PARTY", "sentiment": "neutral", "sentiment_score": 0.0, "framing": "neutral", "context_snippet": "RSP's Rabi Lamichhane...issued statements"},
        ],
    },
]


def seed(conn, demo: bool = False):
    cur = conn.cursor()

    # ── Media Sources ──────────────────────────────────────
    print("Seeding media sources...")
    for src in MEDIA_SOURCES:
        cur.execute(
            """
            INSERT INTO media_sources (id, name, slug, base_url, rss_feed_url, logo_url, is_active, avg_bias_score, total_articles)
            VALUES (%(id)s, %(name)s, %(slug)s, %(base_url)s, %(rss_feed_url)s, %(logo_url)s, %(is_active)s, %(avg_bias_score)s, %(total_articles)s)
            ON CONFLICT (slug) DO NOTHING
            """,
            src,
        )
    conn.commit()
    print(f"  ✓ {len(MEDIA_SOURCES)} media sources seeded")

    if not demo:
        print("\nDone. Run with --demo to also insert sample articles.")
        return

    # ── Demo Event ─────────────────────────────────────────
    print("\nSeeding demo event cluster...")
    cur.execute(
        """
        INSERT INTO events (id, title, summary, bias_divergence_score, article_count)
        VALUES (%(id)s, %(title)s, %(summary)s, %(bias_divergence_score)s, %(article_count)s)
        ON CONFLICT DO NOTHING
        """,
        DEMO_EVENT,
    )

    # ── Source slug → ID lookup ────────────────────────────
    cur.execute("SELECT id, slug FROM media_sources")
    source_map = {row[1]: row[0] for row in cur.fetchall()}

    # ── Demo Articles + LLM Outputs + Entities ─────────────
    print("Seeding demo articles...")
    demo_article_ids = []
    for i, (art, llm) in enumerate(zip(DEMO_ARTICLES, DEMO_LLM_OUTPUTS)):
        article_id = str(uuid.uuid4())
        demo_article_ids.append(article_id)
        published_at = datetime.utcnow() - timedelta(hours=random.randint(1, 48))

        cur.execute(
            """
            INSERT INTO articles
              (id, url, title, content, author, published_at, source_id, event_id,
               bias_score, is_analyzed, is_clustered)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,true)
            ON CONFLICT (url) DO NOTHING
            """,
            (
                article_id,
                f"https://demo.vantage.np/article/{article_id}",
                art["title"],
                art["content"],
                art["author"],
                published_at,
                source_map[art["source_slug"]],
                DEMO_EVENT["id"],
                art["bias_score"],
            ),
        )

        # LLM output
        raw_output = {
            "entities": llm["entities"],
            "bias_score": art["bias_score"],
            "framing_analysis": llm["framing_analysis"],
            "bias_reasoning": llm["bias_reasoning"],
            "event_summary": llm["event_summary"],
            "overall_sentiment": "mixed",
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "latency_ms": random.randint(800, 2400),
        }
        llm_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO llm_outputs
              (id, article_id, provider, model_name, raw_output,
               framing_analysis, event_summary, bias_reasoning, latency_ms)
            VALUES (%s,%s,'openai','gpt-4o-mini',%s,%s,%s,%s,%s)
            ON CONFLICT (article_id) DO NOTHING
            """,
            (
                llm_id,
                article_id,
                json.dumps(raw_output),
                llm["framing_analysis"],
                llm["event_summary"],
                llm["bias_reasoning"],
                raw_output["latency_ms"],
            ),
        )

        # Entities
        for ent_data in llm["entities"]:
            # Upsert entity
            entity_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO entities (id, name, entity_type, is_political)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (name) DO UPDATE SET entity_type = EXCLUDED.entity_type
                RETURNING id
                """,
                (entity_id, ent_data["name"], ent_data["type"]),
            )
            real_entity_id = cur.fetchone()[0]

            ae_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO article_entities
                  (id, article_id, entity_id, sentiment, sentiment_score, framing, context_snippet)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (article_id, entity_id) DO NOTHING
                """,
                (
                    ae_id,
                    article_id,
                    real_entity_id,
                    ent_data["sentiment"],
                    ent_data["sentiment_score"],
                    ent_data["framing"],
                    ent_data["context_snippet"],
                ),
            )

    conn.commit()
    print(f"  ✓ {len(DEMO_ARTICLES)} demo articles with LLM outputs seeded")

    # Update source stats
    cur.execute("""
        UPDATE media_sources ms SET
          avg_bias_score = sub.avg_bias,
          total_articles = sub.cnt
        FROM (
          SELECT source_id, AVG(bias_score) as avg_bias, COUNT(*) as cnt
          FROM articles WHERE bias_score IS NOT NULL
          GROUP BY source_id
        ) sub
        WHERE ms.id = sub.source_id
    """)
    conn.commit()
    print("  ✓ Source stats updated")
    print("\n✅ Demo seed complete. Open http://localhost:3000 to explore VANTAGE.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Insert demo articles")
    args = parser.parse_args()

    print(f"Connecting to: {DB_URL}")
    try:
        conn = psycopg2.connect(DB_URL)
        seed(conn, demo=args.demo)
        conn.close()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure PostgreSQL is running and migrations have been applied:")
        print("  docker-compose up -d postgres")
        print("  cd backend && alembic upgrade head")
        sys.exit(1)
