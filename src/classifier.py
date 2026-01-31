"""ML-based category classifier using sentence embeddings and actor metadata."""

from __future__ import annotations

import numpy as np
from apify import Actor
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .categories import CATEGORY_EXEMPLARS, CATEGORIES


class CategoryClassifier:
    """Classifies Actors into categories using semantic similarity and metadata signals."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the classifier with a sentence transformer model.

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model = SentenceTransformer(model_name)
        self._exemplar_embeddings: dict[str, np.ndarray] = {}
        self._initialize_exemplars()

    def _initialize_exemplars(self) -> None:
        """Pre-compute embeddings for all category exemplars."""
        for category, exemplars in CATEGORY_EXEMPLARS.items():
            embeddings = self.model.encode(exemplars, convert_to_numpy=True)
            self._exemplar_embeddings[category] = embeddings

    def _build_rich_text(self, actor: dict) -> str:
        """
        Build a rich text representation of an actor using all available data.

        This combines title, description, categories, username, pricing info,
        and other metadata into a comprehensive text for embedding.
        """
        parts = []

        # Core text content
        title = actor.get("title", "")
        description = actor.get("description", "")
        if title:
            parts.append(f"Title: {title}")
        if description:
            parts.append(f"Description: {description}")

        # Username/author can indicate actor type (some authors specialize in AI/agents)
        username = actor.get("username", "")
        user_full_name = actor.get("userFullName", "")
        if user_full_name:
            parts.append(f"Author: {user_full_name}")
        elif username:
            parts.append(f"Author: {username}")

        # NOTE: We intentionally DO NOT include existing categories
        # The goal is to classify based on content, not existing (unreliable) categories

        # Pricing model can indicate actor sophistication
        pricing_info = actor.get("currentPricingInfo", {})
        pricing_model = pricing_info.get("pricingModel", "")
        if pricing_model:
            # Map pricing models to descriptive text
            pricing_descriptions = {
                "FREE": "Free to use",
                "PAY_PER_EVENT": "Pay per event pricing with usage-based billing",
                "PRICE_PER_DATASET_ITEM": "Price per data item extracted",
                "FLAT_PRICE_PER_MONTH": "Subscription-based monthly pricing",
            }
            pricing_desc = pricing_descriptions.get(pricing_model, pricing_model)
            parts.append(f"Pricing: {pricing_desc}")

        # Agentic payments flag is a strong signal for AGENTS category
        if actor.get("isWhiteListedForAgenticPayments"):
            parts.append("Supports agentic payments and AI agent integration")

        # Badge can indicate special status
        badge = actor.get("badge")
        if badge:
            parts.append(f"Badge: {badge}")

        # Notice field sometimes contains useful info
        notice = actor.get("notice")
        if notice and notice != "NONE":
            parts.append(f"Notice: {notice}")

        return "\n".join(parts)

    def _compute_metadata_scores(self, actor: dict) -> dict[str, float]:
        """
        Compute category score adjustments based on metadata signals.

        Returns a dict of category -> score adjustment (can be positive or negative).
        """
        adjustments: dict[str, float] = {cat: 0.0 for cat in CATEGORIES}

        title = (actor.get("title") or "").lower()
        description = (actor.get("description") or "").lower()
        text = f"{title} {description}"

        # === AGENTS category: Very strict filtering ===
        # The AGENTS category in the API is full of mis-categorized scrapers.
        # We need to be VERY strict about what qualifies as a true AI agent.

        # DISQUALIFYING keywords - these CANNOT be AI agents
        disqualifiers = [
            "scraper", "scraping", "crawler", "crawling", "extractor", "extraction",
            "downloader", "download", "transcript", "expander", "redirects",
            "filings", "filing", "property", "real estate", "listings",
            "comments scraper", "profile scraper", "templates scraper",
        ]

        is_disqualified = False
        for kw in disqualifiers:
            if kw in title:
                adjustments["AGENTS"] -= 3.0
                is_disqualified = True
                break

        # === Check for AI agent signals FIRST ===
        # Tier 1: Very strong signals - these are definitely AI agents
        tier1_signals = [
            "browse the web", "browsing the web", "natural language prompts",
            "autonomous agent", "agentic", "tool calling", "function calling",
            "mcp server", "model context protocol",
        ]

        # Tier 2: Good signals - likely AI agents
        tier2_signals = [
            "natural language", "llm", "gpt", "openai", "claude", "anthropic",
            "ai-powered", "ai powered", "autonomous", "reasoning",
            "interact with", "langchain", "langgraph",
        ]

        has_tier1_signal = any(sig in text for sig in tier1_signals)
        has_tier2_signal = any(sig in text for sig in tier2_signals)

        # Description disqualifiers - penalize scraping-focused actors
        # BUT only if they don't have strong AI agent signals
        if not is_disqualified and not has_tier1_signal:
            desc_disqualifiers = [
                "scrapes", "scraping", "crawls", "crawling", "extracts data",
                "extract data", "collect data", "gathers data", "fetch data",
                "follows redirects", "resolved url", "redirect chain",
                "scrape", "extract", "extraction",
            ]
            penalty_count = 0
            for kw in desc_disqualifiers:
                if kw in description:
                    penalty_count += 1
            # Apply cumulative penalty for scraping focus - heavy penalty
            adjustments["AGENTS"] -= min(penalty_count * 0.6, 2.0)

        # === REQUIRED signals for TRUE AI agents ===
        # A true AI agent MUST have at least one of these signals
        # (tier signals already computed above)

        # "agent" in title without disqualifiers is a medium signal
        has_agent_in_title = "agent" in title and not is_disqualified

        if has_tier1_signal:
            # Tier 1 signals get big boost
            adjustments["AGENTS"] += 1.5
            if has_agent_in_title:
                adjustments["AGENTS"] += 0.5
        elif has_tier2_signal:
            # Tier 2 signals get medium boost
            adjustments["AGENTS"] += 0.8
            if has_agent_in_title:
                adjustments["AGENTS"] += 0.3
        elif has_agent_in_title:
            # "agent" in title but no AI signal - very weak boost
            adjustments["AGENTS"] += 0.1
        else:
            # No agent signals at all - penalize
            adjustments["AGENTS"] -= 0.8

        # Additional AI agent keywords for extra boost
        agent_keywords = [
            "web agent", "browser agent", "research agent",
            "autonomous agent", "ai agent", "intelligent agent",
            "chain of thought", "decision making", "plans and executes",
        ]
        for kw in agent_keywords:
            if kw in text:
                adjustments["AGENTS"] += 0.3

        # isWhiteListedForAgenticPayments is a strong signal
        if actor.get("isWhiteListedForAgenticPayments"):
            adjustments["AGENTS"] += 0.8
            adjustments["AI"] += 0.1
            adjustments["MCP_SERVERS"] += 0.2

        # === MCP_SERVERS category: Must explicitly mention MCP ===
        mcp_keywords = ["mcp", "model context protocol", "mcp server", "mcp client"]
        has_mcp_keyword = any(kw in text for kw in mcp_keywords)

        if has_mcp_keyword:
            # Boost MCP score if explicitly mentions MCP
            adjustments["MCP_SERVERS"] += 0.5
        else:
            # Penalize heavily if no MCP mention - it's probably not an MCP server
            adjustments["MCP_SERVERS"] -= 0.8

        # Pricing model signals
        pricing_info = actor.get("currentPricingInfo", {})
        pricing_model = pricing_info.get("pricingModel", "")

        # Check for MCP-related pricing events
        pricing_per_event = pricing_info.get("pricingPerEvent", {})
        actor_charge_events = pricing_per_event.get("actorChargeEvents", {})
        # actorChargeEvents can be a dict with event names as keys
        if isinstance(actor_charge_events, dict):
            for event_name, event_data in actor_charge_events.items():
                event_title = str(event_name).lower()
                event_desc = ""
                if isinstance(event_data, dict):
                    event_desc = (event_data.get("eventDescription") or "").lower()
                # Look for MCP/agent-related event names
                if any(kw in event_title or kw in event_desc for kw in ["mcp", "agent", "tool call", "function call"]):
                    adjustments["MCP_SERVERS"] += 0.15
                    adjustments["AGENTS"] += 0.15
                    break  # Only apply once

        return adjustments

    def encode_text(self, text: str) -> np.ndarray:
        """Encode a single text string to embedding."""
        return self.model.encode(text, convert_to_numpy=True)

    def encode_batch(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Encode multiple texts to embeddings."""
        return self.model.encode(
            texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False
        )

    def get_category_scores(self, text: str) -> dict[str, float]:
        """
        Compute similarity scores for all categories based on text.

        Args:
            text: Rich text representation of the actor

        Returns:
            Dict mapping category names to similarity scores
        """
        text_embedding = self.encode_text(text).reshape(1, -1)
        scores = {}

        for category, exemplar_embeddings in self._exemplar_embeddings.items():
            # Compute cosine similarity to all exemplars
            similarities = cosine_similarity(text_embedding, exemplar_embeddings)[0]
            # Use max similarity as category score
            scores[category] = float(np.max(similarities))

        return scores

    def classify_actor(self, actor: dict, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Classify an Actor into categories using all available data.

        Args:
            actor: Full actor dict from Store API
            top_k: Number of top categories to return

        Returns:
            List of (category, score) tuples, sorted by score descending
        """
        # Build rich text from all actor data
        rich_text = self._build_rich_text(actor)

        # Get base scores from semantic similarity
        scores = self.get_category_scores(rich_text)

        # Apply metadata-based adjustments (no cap - let scores differentiate)
        adjustments = self._compute_metadata_scores(actor)
        for category, adjustment in adjustments.items():
            if category in scores:
                scores[category] = scores[category] + adjustment

        # Sort and return top_k
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_k]

    def rerank_actors(
        self, actors: list[dict], category_filter: str | None = None, sort: bool = True
    ) -> list[dict]:
        """
        Compute ML scores for actors and optionally re-rank them.

        Uses batch encoding and matrix multiplications for efficient computation.

        Args:
            actors: List of full actor dicts from Store API
            category_filter: Optional category to prioritize for ranking score
            sort: Whether to sort by ML score (False preserves original order)

        Returns:
            List of actors with added '_ml_scores' and '_ml_rank_score' fields
        """
        if not actors:
            return actors

        num_actors = len(actors)
        Actor.log.info(f"[ML] Starting ML scoring for {num_actors} actors...")

        # Step 1: Build rich text for all actors
        Actor.log.info("[ML] Step 1/5: Building rich text representations...")
        texts = [self._build_rich_text(actor) for actor in actors]
        Actor.log.info(f"[ML] Step 1/5: Done building {len(texts)} text representations")

        # Step 2: Batch encode all texts at once (much faster than individual encoding)
        Actor.log.info(f"[ML] Step 2/5: Encoding {num_actors} texts (this is the slow part)...")
        actor_embeddings = self.encode_batch(texts)  # Shape: (num_actors, embedding_dim)
        Actor.log.info(f"[ML] Step 2/5: Done encoding, shape: {actor_embeddings.shape}")

        # Step 3: Compute all category scores via matrix multiplication
        # For each category, we have exemplar embeddings of shape (num_exemplars, embedding_dim)
        # We want max similarity to any exemplar for each actor-category pair
        category_names = list(self._exemplar_embeddings.keys())
        all_scores = np.zeros((len(actors), len(category_names)))

        Actor.log.info(f"[ML] Step 3/5: Computing similarity scores for {len(category_names)} categories...")
        for cat_idx, category in enumerate(category_names):
            exemplar_embs = self._exemplar_embeddings[category]  # (num_exemplars, embedding_dim)
            # Matrix multiplication: (num_actors, embedding_dim) @ (embedding_dim, num_exemplars)
            # Result: (num_actors, num_exemplars) - similarity of each actor to each exemplar
            similarities = cosine_similarity(actor_embeddings, exemplar_embs)
            # Take max similarity across exemplars for each actor
            all_scores[:, cat_idx] = similarities.max(axis=1)
        Actor.log.info("[ML] Step 3/5: Done computing category similarities")

        # Step 4: Apply metadata adjustments (vectorized where possible)
        Actor.log.info("[ML] Step 4/5: Applying metadata adjustments...")
        for actor_idx, actor in enumerate(actors):
            adjustments = self._compute_metadata_scores(actor)
            for cat_idx, category in enumerate(category_names):
                if category in adjustments:
                    all_scores[actor_idx, cat_idx] += adjustments[category]
        Actor.log.info("[ML] Step 4/5: Done applying metadata adjustments")

        # Step 5: Assign scores back to actors
        Actor.log.info("[ML] Step 5/5: Assigning scores to actors...")
        for actor_idx, actor in enumerate(actors):
            scores = {cat: float(all_scores[actor_idx, cat_idx]) for cat_idx, cat in enumerate(category_names)}
            actor["_ml_scores"] = scores

            # Compute ranking score
            if category_filter and category_filter in scores:
                actor["_ml_rank_score"] = scores[category_filter]
            else:
                actor["_ml_rank_score"] = float(all_scores[actor_idx].max())

        Actor.log.info(f"[ML] Step 5/5: Done! ML scoring complete for {num_actors} actors")

        # Sort by ML rank score (descending) only if requested
        if sort:
            return sorted(actors, key=lambda x: x.get("_ml_rank_score", 0), reverse=True)
        return actors
