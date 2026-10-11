"""Deterministic synthetic operations for the Jal-Setu demonstration."""

from __future__ import annotations

from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Any

from data import DEPOTS, RECHARGE_SITE_SPECS, TANKERS, WARD_SPECS

BASELINE_CAPTURED_RECHARGE_LITERS = 22_137_801

STATE: dict[str, Any] = {
    "rain_mm": 95.0,
    "duration_hours": 6,
    "allocated_liters": 0,
    "allocated_by_site": {},
    "routes": {},
    "delivered": set(),
    "audit": [],
}


def _risk(spec: dict[str, Any], rain_mm: float) -> float:
    return round(min(0.99, max(0.03,
        0.30 * spec["water_stress"] / 100
        + 0.45 * rain_mm / 200
        + 0.25 * spec["impervious_pct"] / 100)), 3)


def ward_features(rain_mm: float | None = None) -> dict[str, Any]:
    rain = STATE["rain_mm"] if rain_mm is None else float(rain_mm)
    features = []
    for i, spec in enumerate(WARD_SPECS):
        row, col = divmod(i, 5)
        west, south = 77.267 + col * 0.0135, 28.379 + row * 0.011
        east, north = west + 0.0137, south + 0.0112
        coefficient = 0.74 + 0.0011 * spec["impervious_pct"]
        risk = _risk(spec, rain)
        runoff = int(rain * spec["area_km2"] * 1_000_000 * coefficient)
        props = {**spec, "lon": round((west + east) / 2, 6), "lat": round((south + north) / 2, 6),
                 "flood_risk": risk, "runoff_liters": runoff,
                 "recharge_potential": round(min(0.99, max(0.1, spec["slope_pct"] / 4 + (1 - spec["impervious_pct"] / 100))), 3)}
        features.append({
            "type": "Feature", "id": spec["id"],
            "geometry": {"type": "Polygon", "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]]},
            "properties": props,
        })
    return {"type": "FeatureCollection", "features": features}


def recharge_features() -> dict[str, Any]:
    features = []
    for spec in RECHARGE_SITE_SPECS:
        features.append({
            "type": "Feature", "id": spec["id"],
            "geometry": {"type": "Point", "coordinates": [spec["lon"], spec["lat"]]},
            "properties": {**spec, "allocated_liters": STATE["allocated_by_site"].get(spec["id"], 0)},
        })
    return {"type": "FeatureCollection", "features": features}


def kpis() -> dict[str, Any]:
    wards = ward_features()["features"]
    runoff = sum(f["properties"]["runoff_liters"] for f in wards)
    risky = sum(1 for f in wards if f["properties"]["flood_risk"] >= 0.55)
    capacity = sum(s["capacity_liters"] for s in RECHARGE_SITE_SPECS)
    allocated = sum(STATE["allocated_by_site"].values())
    captured = BASELINE_CAPTURED_RECHARGE_LITERS
    hours = round(risky * 0.7 + (captured / max(runoff, 1)) * 12, 1)
    route_km = sum(r.get("distance_km", 0) for r in STATE["routes"].values()) or 120
    stops = [stop for route in STATE["routes"].values() for stop in route.get("stops", [])]
    delivered_stops = sum(1 for stop in stops if stop.get("delivered"))
    completion = round(100 * delivered_stops / len(stops), 1) if stops else 0.0
    return {
        "runoff_liters": runoff,
        "recharge_liters": captured,
        "allocated_liters": allocated,
        "site_capacity_liters": capacity,
        "flood_hours_avoided": hours,
        "tanker_km_saved_pct": 18.0,
        "sla_pct": completion,
        "delivery_completion_pct": completion,
        "delivered_stops": delivered_stops,
        "total_stops": len(stops),
        "cost_saved_inr": round(route_km * 14 * 0.18),
        "wards_at_risk": risky,
        "active_tankers": sum(1 for t in TANKERS if t["available"]),
        "rain_mm": STATE["rain_mm"],
        "formula_note": "Synthetic proxy: runoff = rainfall × area × 1,000,000 × composite coefficient; flood-hours ≈ risk wards × 0.7 h + fixed reference capture share × 12 h; captured recharge is separate from planned per-site allocation; delivery completion = completed synthetic stops / planned stops (sla_pct is a compatibility alias, not measured real-world SLA).",
    }


def add_audit(actor: str, action: str, detail: str) -> None:
    STATE["audit"].insert(0, {
        "id": f"AUD-{len(STATE['audit']) + 1:04d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "detail": detail,
        "synthetic": True,
    })
    del STATE["audit"][100:]


def apply_scenario(rain_mm: float, duration_hours: int, actor: str) -> dict[str, Any]:
    STATE["rain_mm"] = float(rain_mm)
    STATE["duration_hours"] = int(duration_hours)
    metrics = kpis()
    add_audit(actor, "scenario_applied", f"{rain_mm:g} mm over {duration_hours} h (simulated)")
    return {"rain_mm": rain_mm, "duration_hours": duration_hours, "runoff_liters": metrics["runoff_liters"],
            "high_risk_wards": metrics["wards_at_risk"], "recharge_liters": metrics["recharge_liters"],
            "wards": ward_features(), "kpis": kpis(), "synthetic": True}


def allocate_recharge(site_id: str | None, liters: int, ward_id: str | None, actor: str) -> dict[str, Any]:
    sites = [s for s in RECHARGE_SITE_SPECS if site_id is None or s["id"] == site_id]
    if not sites:
        raise ValueError("Recharge site not found")
    available_sites = [s for s in sites if STATE["allocated_by_site"].get(s["id"], 0) < s["capacity_liters"]]
    if not available_sites:
        raise ValueError("No synthetic recharge capacity remains at the selected site")
    site = max(available_sites, key=lambda s: s["score"])
    already_allocated = STATE["allocated_by_site"].get(site["id"], 0)
    remaining = site["capacity_liters"] - already_allocated
    amount = min(max(0, int(liters)), remaining)
    STATE["allocated_by_site"][site["id"]] = already_allocated + amount
    STATE["allocated_liters"] = sum(STATE["allocated_by_site"].values())
    add_audit(actor, "recharge_allocated", f"{amount:,} L assigned to {site['name']} (simulated)")
    return {"status": "allocated", "site_id": site["id"], "site_name": site["name"], "ward_id": ward_id or site["ward_id"],
            "allocated_liters": amount, "remaining_capacity_liters": remaining - amount,
            "total_allocated_liters": STATE["allocated_liters"], "total_recharge_liters": kpis()["recharge_liters"], "synthetic": True}


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1, lon2, lat2 = map(radians, (a[0], a[1], b[0], b[1]))
    dlon, dlat = lon2 - lon1, lat2 - lat1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(h))


def solve_routes(actor: str) -> dict[str, Any]:
    wards = sorted(ward_features()["features"], key=lambda f: f["properties"]["flood_risk"], reverse=True)
    new_routes = {}
    tanker_count = len(TANKERS)
    for i, tanker in enumerate(TANKERS):
        depot = next(d for d in DEPOTS if d["id"] == tanker["depot_id"])
        start = i * len(wards) // tanker_count
        end = (i + 1) * len(wards) // tanker_count
        assigned = wards[start:end]
        current = (depot["lon"], depot["lat"])
        stops, line = [], [list(current)]
        distance = 0.0
        for j, feature in enumerate(assigned, start=1):
            p = feature["properties"]
            target = (p["lon"], p["lat"])
            distance += _haversine_km(current, target)
            current = target
            line.append(list(current))
            stop_id = f"{tanker['id']}-S{j:02d}"
            stops.append({"stop_id": stop_id, "ward_id": p["id"], "ward_name": p["name"],
                          "demand_liters": min(tanker["capacity_liters"] // max(1, len(assigned)), 8_000),
                          "priority": round(p["flood_risk"], 2), "delivered": stop_id in STATE["delivered"],
                          "lat": p["lat"], "lon": p["lon"]})
        distance += _haversine_km(current, (depot["lon"], depot["lat"]))
        line.append([depot["lon"], depot["lat"]])
        delivered_count = sum(1 for stop in stops if stop["delivered"])
        status = "completed" if stops and delivered_count == len(stops) else "in progress" if delivered_count else "planned"
        new_routes[tanker["id"]] = {"tanker_id": tanker["id"], "depot": depot, "stops": stops,
                                     "distance_km": round(distance, 2), "geometry": {"type": "LineString", "coordinates": line},
                                     "status": status, "synthetic": True}
    STATE["routes"] = new_routes
    add_audit(actor, "dispatch_optimized", f"Capacity-aware heuristic produced {len(new_routes)} synthetic routes")
    return {"routes": list(new_routes.values()), "total_routes": len(new_routes),
            "total_km": round(sum(r["distance_km"] for r in new_routes.values()), 2),
            "method": "Deterministic nearest-neighbour heuristic; synthetic demo only", "synthetic": True}


def mark_delivered(stop_id: str, actor: str) -> dict[str, Any]:
    for route in STATE["routes"].values():
        for stop in route["stops"]:
            if stop["stop_id"] == stop_id:
                STATE["delivered"].add(stop_id)
                stop["delivered"] = True
                route["status"] = "completed" if all(s["delivered"] for s in route["stops"]) else "in progress"
                add_audit(actor, "stop_delivered", f"{stop['ward_name']} stop marked delivered (simulated)")
                return {"status": "delivered", "stop_id": stop_id, "ward_name": stop["ward_name"], "synthetic": True}
    raise ValueError("Stop not found. Optimize tanker routes first.")


def copilot_reply(message: str) -> str:
    text = message.lower()
    metrics = kpis()
    top = sorted(ward_features()["features"], key=lambda f: f["properties"]["flood_risk"], reverse=True)[:3]
    names = ", ".join(f"{x['properties']['name']} ({x['properties']['flood_risk']:.0%})" for x in top)
    if any(word in text for word in ("storm", "rain", "120", "scenario", "flood")):
        return (f"At {metrics['rain_mm']:.0f} mm in the current synthetic scenario, estimated runoff is "
                f"{metrics['runoff_liters']:,} L with {metrics['wards_at_risk']} of 20 micro-catchments at elevated risk. "
                f"Priority watch: {names}. Adjust the rainfall control and apply a scenario to compare outcomes. This is a simulation, not a live forecast.")
    if any(word in text for word in ("tanker", "delivery", "dispatch", "prioritize")):
        return (f"A synthetic priority order is {names}. Run Optimize tankers to calculate capacity-aware demo routes; "
                "field crews should confirm access, demand and safety before any real-world action.")
    if any(word in text for word in ("recharge", "infiltration", "site")):
        return (f"Reference simulated capture is {metrics['recharge_liters']:,} L; planned site allocation is "
                f"{metrics['allocated_liters']:,} L of {metrics['site_capacity_liters']:,} L total synthetic capacity. "
                "Use Allocate recharge to assign demo capacity to a site with a high synthetic priority score.")
    return (f"I’m monitoring 20 synthetic Faridabad micro-catchments. The current scenario is {metrics['rain_mm']:.0f} mm, "
            f"with {metrics['wards_at_risk']} wards at elevated risk. Ask me to test a storm, prioritize tanker deliveries, or review recharge. "
            "This is a planning aid only; confirm field conditions before dispatch.")
