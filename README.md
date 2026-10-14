# Jal-Setu Water Resilience Command

A simulated Faridabad urban-water command-centre demo, reconstructed as a self-contained website. It includes a map-first dashboard, synthetic storm what-ifs, recharge allocation, heuristic tanker routing, crew stop actions, impact estimates and a rule-based streaming Copilot.

## Important demo scope

All wards, boundaries, rainfall, demand, route outcomes and impact values are synthetic examples. The interface is a planning aid only—not a live municipal system, weather forecast, dispatch platform, official ward map, or production authentication service. The `demo-admin` and `demo-crew` bearer tokens are intentionally public demo-role selectors, not credentials. State for scenarios, allocations and route completions is in memory and may reset when the service restarts. The replacement does not claim parity with the original LightGBM/OR-Tools components; forecasts and routes use transparent formulas and deterministic heuristics.

## Prerequisites and dependencies

- Python 3.12 and `pip` (the production container uses Python 3.12).
- Internet access for the public MapLibre GL JS CDN, OpenFreeMap map style/tiles, and Google Fonts. The API and the rest of the dashboard run locally without a database.
- Runtime packages, pinned in `requirements.txt`: `fastapi==0.115.6` and `uvicorn[standard]==0.34.0`.
- Test package, pinned in `requirements-test.txt`: `httpx==0.28.1` (the file also installs the runtime packages).

## Run locally

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3000
```

Open `http://localhost:3000`. The server serves the UI and API from the same origin. The public demo role selector switches between ICCC Admin and Field Crew; Field Crew access is limited to T01. The unauthenticated container readiness endpoint is `/_jalsetu/health`.

To run the API checks:

```sh
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
```

## Map and external resources

The map is rendered with MapLibre GL JS using OpenFreeMap's public `positron` style. The map is attributed in the UI to OpenMapTiles and OpenStreetMap contributors. Public map tiles have no stated SLA and require an internet connection. Interface fonts use Manrope and DM Mono via Google Fonts with system fallbacks.

## Deployment

The production container uses `Dockerfile`, listens on `0.0.0.0:$PORT` (default `3000`), and serves static assets, API routes, `/manus-routes.json`, and `/_jalsetu/health` from one origin. The live managed WebDev site is [jalsetu-nbk8dbqi.manus.space](https://jalsetu-nbk8dbqi.manus.space), published from checkpoint `e724854`. Hosting is currently On-Demand: the URL is stable, but the app may sleep after inactivity and cold-start on a later visit. This conversion did not create AWS resources or enable a database.
