"""Main entry point for the Apify Store Searcher Actor."""

from __future__ import annotations

import asyncio
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from apify import Actor

from .cache import store_cache
from .classifier import CategoryClassifier
from .frontend import get_html


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Actor."""

    def log_message(self, format: str, *args) -> None:
        """Override to use Actor.log instead of stderr."""
        Actor.log.debug(format % args)

    def send_json_response(self, data: dict, status: int = 200) -> None:
        """Send a JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_html_response(self, html: str, status: int = 200) -> None:
        """Send an HTML response."""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self) -> None:
        """Handle GET requests."""
        # Handle Apify standby readiness probe
        if "x-apify-container-server-readiness-probe" in self.headers:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "":
            # Serve frontend
            self.send_html_response(get_html())

        elif path == "/api/search":
            # Search API endpoint
            self.handle_search(parsed.query)

        elif path == "/api/cache-stats":
            # Cache statistics endpoint
            self.send_json_response(store_cache.get_cache_stats())

        elif path == "/health":
            # Health check endpoint
            self.send_json_response({"status": "healthy"})

        else:
            self.send_json_response({"error": "Not found"}, status=404)

    def handle_search(self, query_string: str) -> None:
        """Handle the search API endpoint."""
        params = parse_qs(query_string)
        search_query = params.get("q", [""])[0]
        category = params.get("category", [""])[0]
        limit = min(int(params.get("limit", ["50"])[0]), 100)
        offset = int(params.get("offset", ["0"])[0])

        try:
            # Handle search and category filtering
            # - Search within category: filter by both, use ML ranking for category
            # - Search only: filter by search term, keep original order
            # - Category only: use ML ranking for that category
            # - Neither: preserve original store ordering
            if search_query and category:
                # Search within a category - get ML-ranked category results, then filter
                actors = store_cache.get_actors_for_category_ranked(category)
                search_lower = search_query.lower()
                actors = [
                    a for a in actors
                    if search_lower in (a.get("title") or "").lower()
                    or search_lower in (a.get("description") or "").lower()
                    or search_lower in (a.get("username") or "").lower()
                ]
            elif search_query:
                # Search across all actors (filter by search term, keep original order)
                actors, _ = store_cache.get_actors(
                    category="",
                    search=search_query,
                    use_ranked=False,
                )
            elif category:
                # Category browsing - re-rank by category-specific ML score
                actors = store_cache.get_actors_for_category_ranked(category)
            else:
                # No search, no category - preserve original store ordering
                actors, _ = store_cache.get_actors(
                    category="",
                    search="",
                    use_ranked=False,
                )

            # Paginate results
            total_count = len(actors)
            actors = actors[offset:offset + limit]

            self.send_json_response({
                "actors": actors,
                "total": total_count,
                "limit": limit,
                "offset": offset,
            })

        except Exception as e:
            Actor.log.error(f"Search error: {e}")
            self.send_json_response({"error": str(e)}, status=500)


def run_http_server(port: int) -> None:
    """Run the HTTP server in a separate thread."""
    server = HTTPServer(("0.0.0.0", port), RequestHandler)
    Actor.log.info(f"HTTP server running on port {port}")
    Actor.log.info(f"Open http://localhost:{port} in your browser")
    server.serve_forever()


async def main() -> None:
    """Main entry point for the Actor."""
    async with Actor:
        Actor.log.info("Starting Apify Store Searcher...")

        # Initialize the ML classifier
        Actor.log.info("Loading ML model (this may take a moment on first run)...")
        classifier = CategoryClassifier()
        Actor.log.info("ML model loaded successfully")

        # Set classifier on cache so it can apply ML ranking during refresh
        store_cache.set_classifier(classifier)

        # Initialize the cache - load from KV Store or fetch fresh
        # This MUST complete before we start serving requests
        await store_cache.initialize()
        Actor.log.info("Cache initialized successfully")

        # Get the port from environment (Apify sets ACTOR_STANDBY_PORT for standby mode)
        port = int(os.environ.get("ACTOR_STANDBY_PORT", os.environ.get("PORT", 8080)))

        # Start HTTP server in a separate thread (it's blocking)
        server_thread = threading.Thread(target=run_http_server, args=(port,), daemon=True)
        server_thread.start()

        # Start background cache refresh loop
        Actor.log.info("Starting background cache refresh (every 5 minutes)")
        await store_cache.start_background_refresh()
