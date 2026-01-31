# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Apify Actor - a serverless program that runs on the Apify platform. It uses the Apify SDK for Python to build web scrapers and automation tools.

## Commands

```bash
# Run Actor locally
apify run

# Deploy to Apify platform (requires authentication)
apify login
apify push
```

## Architecture

- `src/main.py` - Main entry point containing the `main()` async function with Actor logic
- `src/__main__.py` - Module runner that executes `main()` via `asyncio.run()`
- `.actor/actor.json` - Actor configuration (name, version, runtime settings)
- `requirements.txt` - Python dependencies (uses Apify SDK <4.0.0)

## Apify Actor Guidelines

**Always use `Actor.log` for logging** - it censors sensitive data automatically.

**Key patterns:**
- Use `async with Actor:` context manager in main function
- Use `Actor.push_data()` to store output in datasets
- Use `Actor.set_value()` / `Actor.get_value()` for key-value store
- Validate input early and fail gracefully
- Use CheerioCrawler for static HTML (faster), PlaywrightCrawler only for JS-heavy sites

**Don't:**
- Rely on `Dataset.getInfo()` for final counts on Cloud
- Hard code values that should be in input schema
- Disable standby mode without explicit permission

See [AGENTS.md](AGENTS.md) for complete Apify development guidelines including input/output schema specifications.
