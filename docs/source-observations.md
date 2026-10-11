# Jal-Setu Source Observations (Synthetic Demo)

## Sources and recovery boundary

- Original demo URL: https://8000-ii16o3z0zbprjp0zasvm4-d924d87e.sg2.manus.computer/
- Original OpenAPI URL: https://8000-ii16o3z0zbprjp0zasvm4-d924d87e.sg2.manus.computer/openapi.json
- After implementation planning, direct requests to both the original homepage and its API began returning HTTP 502. The already-loaded original app remained available in the browser long enough to inspect visible views. The production JS/CSS bundle and complete API schemas/data were not saved; do not treat this page capture as source code.
- The Command, Dispatch and Impact screenshots were inspected in the original browser session but are not shipped with this repository. Text below records only the visible dashboard content at capture time.

## Command view

Observed brand/header: “JAL-SETU · WATER RESILIENCE GRID”; location “FARIDABAD / HR”; “SYSTEM NOMINAL”; navigation Command / Dispatch / Impact; actions “Allocate recharge” and “Optimize tankers”. The dashboard describes a “Water command centre” for “Urban flood response · Managed recharge · Essential water delivery”. The map shows “LIVE CITY MODEL · 20 MICRO-CATCHMENTS” and layers Flood risk, Water stress, Recharge potential; visible map caption is 28.41° N · 77.31° E. The scenario panel exposes a 0–200 mm rainfall slider, duration choices 1/3/6/12 hours and Apply scenario.

At one observed 95 mm scenario, the visible response picture showed runoff about 3.43 billion L, 18/20 at-risk wards, about 22.1M L recharge and 12 active tankers. The top ward watch included Greenfield 04 (87.9% water stress), Greenfield 19 (98%) and NIT 01 (65.7%). The lower cards showed 22.14M L managed recharge capacity, 12.7 flood hours avoided (estimated), and 18% tanker distance saved (baseline comparison). The interface labels the data synthetic/demo.

## Dispatch and impact views

Dispatch screen heading: “Tanker dispatch”; caption “CAPACITY-AWARE ROUTING · 12 VEHICLES”; initial state “Dispatch not solved yet” with “Run Optimize tankers to compute routes”, plus “Re-solve”. The shared map, scenario panel and ward watch remain visible.

Impact screen heading: “Scenario impact”. It showed Recharge per event 22.1M L (captured · simulated), Flood-hours avoided 12.7 h (estimated proxy), Tanker distance saved 18% and ₹303 estimated cost saved, SLA coverage 100% (delivery windows met). Its visible formula descriptions were: runoff = rain mm × area km² × 1,000,000 × composite runoff coefficient; recharge = sum of minimum(site capacity, runoff share × piezometric-priority weight); flood-hours avoided ≈ high-risk wards × 0.7 h + captured-runoff share × 12 h; travel/cost saved = optimized route km × ₹14/km × 18% assumed saving; SLA = stops within delivery window ÷ planned stops. The old screen stated “LightGBM · R² 0.9781 · MAE 1,38,70,642 L · synthetic training data”; that exact model cannot be verified or reproduced from the now-inaccessible backend and is intentionally not claimed by the replacement.

## Partial API contract observed earlier

Endpoint families and paths noted before the host became unavailable: `/health`, `/api/wards`, `/api/hotspots`, `/api/simulate`, `/api/recharge/sites`, `/api/recharge/allocate`, `/api/tankers`, `/api/dispatch/solve`, `/api/dispatch/routes/{tanker_id}`, `/api/dispatch/stops/{stop_id}/delivered`, `/api/kpis`, `/api/audit`, `/api/model/metrics`, and `/api/copilot/chat`. Request/response details beyond these names are not complete; the new frontend and backend therefore share a newly defined synthetic contract. Demo tokens are public role selectors only, not real authentication.
