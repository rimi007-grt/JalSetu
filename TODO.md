# Jal-Setu Permanent Website — Outcome ToDo

## Stable public website
- [ ] Turn the existing Jal-Setu Water Resilience Command demo into a permanent public website with a stable hosted URL. Recreate its Faridabad simulated command-centre experience from the visible UI captures and observed API facts; clearly mark data and outcomes as synthetic/demo, and do not depend on the temporary preview host for frontend or API behavior.

## Map and storm-scenario experience
- [x] Recreate the dark geospatial operations dashboard and interactive city map with flood-risk, water-stress, and recharge-potential layers. Keep rainfall what-if controls and scenario application; update the ward watch and response KPIs from the selected simulated scenario. Include map-provider and data-source attribution.

## Recharge and tanker operations
- [x] Implement visible equivalents of managed-recharge allocation, tanker route optimization, route display, and field-crew stop completion actions. Keep admin and crew views with role-scoped behavior; demo role credentials and simulated operations must not be presented as production authentication or live municipal dispatch.

## Response metrics and Copilot
- [x] Recreate the impact metrics and rule-based streaming Jal-Setu Copilot. Copilot responses and operational recommendations must be grounded in the dashboard's synthetic demo context, remind users to confirm field conditions before dispatch, and describe any replacement forecasting/routing as synthetic rather than claiming unverifiable LightGBM/OR-Tools parity.

## Durable serving
- [x] Serve the frontend and API from the same managed WebDev site origin, with an independent synthetic demo API shaped by the captured route list and partial public contract rather than proxied to the temporary backend. Run the server on `0.0.0.0:$PORT` (default port 3000), provide an unauthenticated `/_jalsetu/health` response, and publish the `/manus-routes.json` page manifest. Do not enable a database or deploy AWS resources for this conversion.

## Canonical checkpoint and publication
- [ ] Publish a canonical checkpoint and confirm successful WebDev publication before reporting the permanent URL.
