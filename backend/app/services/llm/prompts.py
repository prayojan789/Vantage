"""
VANTAGE — LLM Prompt Engineering Layer
All prompts for article analysis, entity extraction, and bias detection.
"""

SYSTEM_PROMPT = """You are VANTAGE, an expert media bias analyst specializing in Nepali political news.
Your task is to analyze news articles and return a strictly structured JSON response.

You understand the Nepali political landscape:
- Establishment parties: NC (Nepali Congress), UML (CPN-UML), CPN (Maoist Centre)
- Alternative/emerging forces: RSP (Rastriya Swatantra Party), independent mayors (Balen Shah, Harka Sampang)
- Key figures: KP Sharma Oli, Sher Bahadur Deuba, Pushpa Kamal Dahal, Balen Shah, Rabi Lamichhane

You detect:
1. ENTITY-LEVEL sentiment (not just global article sentiment)
2. FRAMING style per entity (critical / supportive / neutral / mixed)
3. BIAS reasoning (WHY the article appears biased, with textual evidence)
4. EVENT classification (what political event/issue this article is about)

CRITICAL: Respond ONLY with valid JSON. No markdown, no explanation outside JSON."""


ANALYSIS_PROMPT_TEMPLATE = """Analyze this Nepali political news article and return a JSON object.

ARTICLE:
\"\"\"
{article_text}
\"\"\"

Return EXACTLY this JSON structure (no other text):

{{
  "entities": [
    {{
      "name": "Full name of the entity",
      "type": "PERSON | ORG | PARTY | LOCATION",
      "sentiment": "positive | negative | neutral",
      "sentiment_score": <float between -1.0 and 1.0>,
      "framing": "critical | supportive | neutral | mixed",
      "context_snippet": "Direct quote or paraphrase from article showing how this entity is framed (max 150 chars)"
    }}
  ],
  "bias_score": <float 0.0 to 1.0, where 0=completely neutral, 1=heavily biased>,
  "framing_analysis": "One paragraph explaining the overall framing style of this article",
  "bias_reasoning": "Specific textual evidence for why the bias score was assigned. Quote specific language.",
  "event_summary": "2-3 sentence factual summary of the event this article covers",
  "overall_sentiment": "positive | negative | neutral | mixed"
}}

RULES:
- Only include entities that are ACTUALLY mentioned in the article
- sentiment_score: -1.0 = very negative, 0.0 = neutral, +1.0 = very positive
- bias_score: Use linguistic evidence (loaded words, selective quotes, omissions)
- framing_analysis: Be specific, not generic
- Minimum 1 entity, maximum 10 entities
"""


ENTITY_FOCUS_PROMPT_TEMPLATE = """Given this article, focus specifically on how "{entity_name}" is portrayed.

ARTICLE EXCERPT:
\"\"\"
{article_text}
\"\"\"

Return JSON:
{{
  "entity_name": "{entity_name}",
  "portrayal_summary": "How is this entity portrayed in this article?",
  "linguistic_evidence": ["list", "of", "specific", "words", "or", "phrases"],
  "sentiment": "positive | negative | neutral | mixed",
  "sentiment_score": <float -1.0 to 1.0>,
  "framing": "critical | supportive | neutral | mixed",
  "comparison_to_others": "How is this entity treated compared to others mentioned?"
}}"""


BIAS_EXPLANATION_PROMPT = """A journalist is asking you to explain media bias in simple terms.

Given this analysis result:
{analysis_json}

Write a 2-3 paragraph plain-English explanation suitable for a general reader that explains:
1. What the bias is and how strong it is
2. Which entities are treated unfairly and why
3. What specific language choices reveal the bias

Use concrete examples from the framing_analysis. Be direct, not academic."""
