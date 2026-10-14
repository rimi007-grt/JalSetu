# Devpost Project Description

**Project name:** Jal-Setu — Water Resilience Command

## Description (copy/paste)

Urban water teams need to weigh flood risk, water stress, and response capacity together. **Jal-Setu** is an interactive command-centre demo for exploring that workflow in Faridabad. It presents a map of 20 synthetic ward catchments with flood-risk, water-stress, and recharge-potential layers. Operators can change a hypothetical rainfall scenario, review ward priorities, allocate simulated recharge, and compute transparent heuristic tanker routes across 12 modeled vehicles. A Field Crew view is limited to its assigned route and can record synthetic stop-completion actions. An impact panel distinguishes captured baseline values from new allocations and reports estimated effects, while a rule-based Copilot streams short briefings based on the active scenario.

The site uses Python and FastAPI for its API, plain HTML/CSS/JavaScript for the dashboard, MapLibre GL JS for mapping, and OpenFreeMap for public map tiles.

**Demo scope:** Locations, forecasts, metrics, and actions are synthetic. Jal-Setu has no live municipal feeds and does not dispatch real crews or tankers. Demo state is held in memory and can reset when the service restarts.

## Project links

- **Live demo:** https://jalsetu-nbk8dbqi.manus.space/
- **Source code:** https://github.com/rimi007-grt/JalSetu
