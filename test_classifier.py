"""Test the classifier to ensure AGENTS and MCP_SERVERS categories rank correctly."""

import httpx

from src.classifier import CategoryClassifier


def fetch_actors_from_api(category: str, limit: int = 1000) -> list[dict]:
    """Fetch actors from a category directly from API (for testing without Actor context)."""
    url = "https://api.apify.com/v2/store"
    params = {"category": category, "limit": limit}
    with httpx.Client(timeout=60.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    return data.get("data", {}).get("items", [])


def test_agents_category():
    """Test the classifier ranking logic for AGENTS category."""
    print("=" * 80)
    print("TESTING AGENTS CATEGORY")
    print("=" * 80)

    print("\nLoading classifier...")
    classifier = CategoryClassifier()
    print("Classifier loaded.\n")

    print("Fetching actors from AGENTS category...")
    actors = fetch_actors_from_api("AGENTS")
    print(f"Fetched {len(actors)} actors.\n")

    # Apply ML re-ranking
    print("Applying ML re-ranking...")
    ranked_actors = classifier.rerank_actors(actors, category_filter="AGENTS")

    # Display top 15 results
    print("\n" + "=" * 80)
    print("TOP 15 AGENTS AFTER ML RE-RANKING:")
    print("=" * 80)

    # Define what should NOT be at the top (scrapers)
    bad_actors = [
        "scraper",
        "crawler",
        "extractor",
        "transcript",
        "expander",
        "filings",
    ]

    top_15_titles = []
    for i, actor in enumerate(ranked_actors[:15], 1):
        title = actor.get("title", "Unknown")
        desc = actor.get("description", "")[:80]
        score = actor.get("_ml_rank_score", 0)
        top_15_titles.append(title.lower())

        # Check if this is a bad actor in top positions
        is_bad = any(bad in title.lower() for bad in bad_actors)
        marker = " ❌ SCRAPER!" if is_bad else ""

        print(f"{i:2}. [{score:.3f}] {title}{marker}")
        print(f"    {desc}...")
        print()

    # Validation
    print("=" * 80)
    print("VALIDATION:")
    print("=" * 80)

    # Check for scrapers in top 10
    scrapers_in_top_10 = 0
    for title in top_15_titles[:10]:
        if any(bad in title for bad in bad_actors):
            scrapers_in_top_10 += 1

    if scrapers_in_top_10 == 0:
        print("✅ No scrapers in top 10!")
    else:
        print(f"❌ Found {scrapers_in_top_10} scrapers in top 10")

    # Check if "AI Web Agent" is in top 5
    ai_web_agent_position = None
    for i, title in enumerate(top_15_titles, 1):
        if "ai web agent" in title:
            ai_web_agent_position = i
            break

    if ai_web_agent_position and ai_web_agent_position <= 5:
        print(f"✅ 'AI Web Agent' is at position {ai_web_agent_position}")
    elif ai_web_agent_position:
        print(f"⚠️  'AI Web Agent' is at position {ai_web_agent_position} (should be top 5)")
    else:
        # Search in all results
        for i, actor in enumerate(ranked_actors, 1):
            if "ai web agent" in actor.get("title", "").lower():
                print(f"⚠️  'AI Web Agent' found at position {i} (should be top 5)")
                break
        else:
            print("❌ 'AI Web Agent' not found in results")

    print("\n" + "=" * 80)
    print("BOTTOM 10 (should be scrapers):")
    print("=" * 80)

    for i, actor in enumerate(ranked_actors[-10:], len(ranked_actors) - 9):
        title = actor.get("title", "Unknown")
        score = actor.get("_ml_rank_score", 0)
        is_scraper = any(bad in title.lower() for bad in bad_actors)
        marker = " ✅" if is_scraper else ""
        print(f"{i:2}. [{score:.3f}] {title}{marker}")


def test_mcp_servers_category():
    """Test the classifier ranking logic for MCP_SERVERS category."""
    print("\n\n" + "=" * 80)
    print("TESTING MCP_SERVERS CATEGORY")
    print("=" * 80)

    print("\nLoading classifier...")
    classifier = CategoryClassifier()
    print("Classifier loaded.\n")

    print("Fetching actors from MCP_SERVERS category...")
    actors = fetch_actors_from_api("MCP_SERVERS")
    print(f"Fetched {len(actors)} actors.\n")

    # Apply ML re-ranking
    print("Applying ML re-ranking...")
    ranked_actors = classifier.rerank_actors(actors, category_filter="MCP_SERVERS")

    # Display top 15 results
    print("\n" + "=" * 80)
    print("TOP 15 MCP_SERVERS AFTER ML RE-RANKING:")
    print("=" * 80)

    mcp_keywords = ["mcp", "model context protocol"]

    top_15_titles = []
    for i, actor in enumerate(ranked_actors[:15], 1):
        title = actor.get("title", "Unknown")
        desc = actor.get("description", "")[:80]
        score = actor.get("_ml_rank_score", 0)
        top_15_titles.append(title.lower())

        # Check if this mentions MCP
        text = f"{title} {desc}".lower()
        has_mcp = any(kw in text for kw in mcp_keywords)
        marker = " ✅ MCP" if has_mcp else " ❌ NO MCP MENTION"

        print(f"{i:2}. [{score:.3f}] {title}{marker}")
        print(f"    {desc}...")
        print()

    # Validation
    print("=" * 80)
    print("VALIDATION:")
    print("=" * 80)

    # Check how many of top 10 mention MCP
    mcp_in_top_10 = 0
    for i, actor in enumerate(ranked_actors[:10], 1):
        title = actor.get("title", "")
        desc = actor.get("description", "")
        text = f"{title} {desc}".lower()
        if any(kw in text for kw in mcp_keywords):
            mcp_in_top_10 += 1

    if mcp_in_top_10 >= 8:
        print(f"✅ {mcp_in_top_10}/10 of top 10 mention MCP")
    else:
        print(f"⚠️  Only {mcp_in_top_10}/10 of top 10 mention MCP")


if __name__ == "__main__":
    test_agents_category()
    test_mcp_servers_category()
