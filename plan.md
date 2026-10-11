# Jal-Setu Permanent Website — Implementation Plan

## Goal and scope

Turn the existing Jal-Setu Water Resilience Command demo into a permanent public website with a stable hosted URL. Recreate its Faridabad simulated command-centre experience and visual identity: interactive flood-risk, water-stress and recharge-potential map layers; rainfall scenario controls; ward watch and response KPIs; managed recharge allocation; tanker optimization and field-crew stop actions; impact metrics; admin/crew views; and the rule-based streaming Copilot. Clearly mark data and outcomes as synthetic/demo, and ensure the new site does not depend on the temporary preview host.

The original repository is unavailable, and after plan approval the temporary host began returning 502 for direct bundle/API downloads. The already-open dashboard remains visible, and its Command, Dispatch and Impact screens plus partial API route/data facts were captured. This is therefore an approximate reconstruction from screenshots, page text and partial API observations, not a copy of the production frontend. The UI will be rebuilt in readable HTML/CSS/JavaScript and the API reimplemented from captured contracts and observed behavior. Exact source, detail-level visual parity and the prior LightGBM/OR-Tools algorithms cannot be verified; the replacement will use transparent synthetic forecasting and heuristic recharge/tanker logic and will not claim those original components.

## Product and interaction design

- **Design movement:** Dark geospatial operations console, closer to a municipal incident-command dashboard than a generic SaaS admin template.
- **Core principles:** Map-first situational awareness; dense but legible operational metrics; a clear distinction between live-like display and simulated data; fast, reversible scenario/dispatch actions.
- **Color philosophy:** Deep forest/charcoal surfaces establish an instrument-panel feel; mint/teal identifies water and active systems; amber/orange marks elevated risk; restrained red is reserved for severe warnings. Maintain high contrast and avoid decorative color noise.
- **Layout paradigm:** Asymmetric command layout: a broad central city map, a narrow scenario/KPI rail, and a persistent Copilot/operations rail. On small screens, stack these panes without hiding core actions.
- **Signature elements:** Ward-boundary overlays and site markers; compact monospace telemetry; small status lights and restrained hazard bands.
- **Interaction and motion:** Scenario controls respond immediately and explain that results are simulated. Map layer changes and panels stay direct; use brief status transitions and subtle pulses only for active-system indicators. Respect reduced-motion preferences.
- **Typography:** Use Manrope for interface text and DM Mono for telemetry with robust system fallbacks; keep labels compact and readings tabular.
- **Brand essence:** “A practical command picture for urban water resilience, built around place and action.” Personality: precise, calm, civic-minded.
- **Brand voice:** Operational and candid. Examples: “Test a storm scenario against the ward map.” / “Simulation only — confirm field conditions before dispatch.”
- **Wordmark/logo:** Recreate the observed Jal-Setu wordmark and compact water/grid mark from the available screen reference; do not imply an official municipal identity.
- **Signature brand color:** Mint/teal, used for healthy water-system status and active controls.

## Implementation approach and project structure

Use one managed WebDev container to serve a readable, single-origin frontend and its API. This keeps `/api/...` calls same-origin and avoids proxying to the temporary demo. The backend will be FastAPI with deterministic synthetic seed data and explicit demo-role checks. It will implement the observed endpoint families for health, wards, hotspots, simulation, recharge, tanker dispatch/routes/delivery, KPIs, audit, model metrics and Copilot. No live municipal, weather or user data will be connected, and no database will be enabled; simulated scenario/action state may reset when the service restarts.

Keep the fixed synthetic reference capture separate from new planned recharge allocations; track allocation against each site's remaining capacity and report it independently. Define delivery completion from marked demo stops over planned demo stops; do not present a constant or actual real-world SLA figure.

Build a new responsive command dashboard from the screenshots and visible text. Use MapLibre GL JS and OpenFreeMap's documented style endpoint (`https://tiles.openfreemap.org/styles/positron`), with visible attribution to OpenFreeMap/OpenMapTiles and OpenStreetMap. The public tile service has no stated SLA, so map rendering is a third-party availability dependency; the dashboard/API remain hosted independently.

Proposed files:

- `main.py` — FastAPI routes, demo-role authorization, static serving, SSE Copilot response and `/_jalsetu/health`.
- `data.py` — clearly synthetic ward, site and tanker seed data shaped to observations captured from the former demo.
- `services.py` — transparent rainfall/runoff estimates, recharge allocation, tanker route heuristics, impact formulas and rule-based Copilot.
- `static/index.html`, `static/styles.css`, `static/app.js` — responsive dashboard, map, controls and client-side rendering; `static/favicon.svg` is the local site icon.
- `static/manus-routes.json` — page route manifest (`/` only; API routes and assets are excluded).
- `tests/` — focused API, role, SSE and synthetic-operation checks.
- `requirements.txt` and `Dockerfile` — pinned Python runtime/dependencies and production entrypoint honoring `PORT` (default 3000).
- `README.md`, `plan.md`, and `TODO.md` — run/deployment notes, approved design/implementation plan, and outcome criteria.

## Build and delivery workflow

Project diagnostics are registered for Python, JSON, HTML, JavaScript and CSS. Implement the API and readable UI, then serve them from the configured port 3000 and verify health, route manifest, static assets, role-scoped endpoints, scenario/dispatch flows and the SSE response. The Docker image installs pinned dependencies, serves on `0.0.0.0:$PORT`, and provides an unauthenticated health response at `/_jalsetu/health`; container publication uses the managed server only, with no separate static build or database. Keep all browser-facing API references relative.

After implementation and affected checks, fetch/integrate the current canonical `main`, commit and push the intended changes to the managed repository, confirm the checkpoint, and use the explicit Publish workflow. Report a permanent URL only after WebDev confirms successful publication. Do not deploy AWS resources as part of this conversion.

## External map reference

- [OpenFreeMap Quick Start](https://openfreemap.org/quick_start/) — MapLibre style URL and integration example.
- [OpenFreeMap](https://openfreemap.org/) — public service and attribution information.
- [MapLibre GL JS documentation](https://www.maplibre.org/maplibre-gl-js/docs/) — vector map library.
