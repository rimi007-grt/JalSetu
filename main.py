from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# The project root is the import root for the standalone backend modules.
import services
from data import DEPOTS, TANKERS

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
app = FastAPI(title="Jal-Setu API", description="Synthetic Faridabad water-resilience demo", version="0.2.0")


class ScenarioRequest(BaseModel):
    rain_mm: float = Field(ge=0, le=200, default=95)
    duration_hours: Literal[1, 3, 6, 12] = 6


class AllocationRequest(BaseModel):
    site_id: str | None = None
    ward_id: str | None = None
    liters: int = Field(default=300_000, ge=0, le=2_000_000)


class DeliveredRequest(BaseModel):
    note: str = ""


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    stream: bool = False


def current_role(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Demo bearer token required")
    token = authorization.removeprefix("Bearer ").strip()
    if token == "demo-admin":
        return "admin"
    if token == "demo-crew":
        return "crew"
    raise HTTPException(status_code=401, detail="Unknown demo role token")


def require_admin(role: str = Depends(current_role)) -> str:
    if role != "admin":
        raise HTTPException(status_code=403, detail={"message": "This simulated operation is restricted to ICCC Admin."})
    return role


def tanker_payload(role: str) -> dict[str, Any]:
    tankers = TANKERS if role == "admin" else [t for t in TANKERS if t["id"] == "T01"]
    return {"tankers": tankers, "depots": DEPOTS, "synthetic": True}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "jal-setu", "city": "Faridabad", "mode": "synthetic-demo", "database": "not-configured"}


@app.get("/_jalsetu/health")
def deploy_health() -> dict[str, str]:
    return {"status": "ok", "service": "jal-setu", "mode": "synthetic-demo"}


@app.get("/manus-routes.json")
def routes_manifest() -> FileResponse:
    return FileResponse(STATIC / "manus-routes.json", media_type="application/json")


@app.get("/api/wards")
def wards(role: str = Depends(current_role)) -> dict[str, Any]:
    return services.ward_features()


@app.get("/api/hotspots")
def hotspots(role: str = Depends(current_role)) -> dict[str, Any]:
    features = services.ward_features()["features"]
    features.sort(key=lambda f: f["properties"]["flood_risk"], reverse=True)
    return {"type": "FeatureCollection", "features": features[:20], "synthetic": True}


@app.post("/api/simulate")
def simulate(payload: ScenarioRequest, role: str = Depends(require_admin)) -> dict[str, Any]:
    return services.apply_scenario(payload.rain_mm, payload.duration_hours, role)


@app.get("/api/recharge/sites")
def recharge_sites(role: str = Depends(current_role)) -> dict[str, Any]:
    return services.recharge_features()


@app.post("/api/recharge/allocate")
def recharge_allocate(payload: AllocationRequest, role: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return services.allocate_recharge(payload.site_id, payload.liters, payload.ward_id, role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc


@app.get("/api/tankers")
def tankers(role: str = Depends(current_role)) -> dict[str, Any]:
    return tanker_payload(role)


@app.post("/api/dispatch/solve")
def dispatch_solve(role: str = Depends(require_admin)) -> dict[str, Any]:
    return services.solve_routes(role)


@app.get("/api/dispatch/routes")
def dispatch_routes(role: str = Depends(current_role)) -> dict[str, Any]:
    routes = services.STATE["routes"]
    if role == "crew":
        routes = {"T01": routes["T01"]} if "T01" in routes else {}
    return {"routes": list(routes.values()), "total_routes": len(routes), "synthetic": True}


@app.get("/api/dispatch/routes/{tanker_id}")
def dispatch_route(tanker_id: str, role: str = Depends(current_role)) -> dict[str, Any]:
    if role == "crew" and tanker_id != "T01":
        raise HTTPException(status_code=403, detail={"message": "Crew route access is limited to T01."})
    route = services.STATE["routes"].get(tanker_id)
    if route is None:
        raise HTTPException(status_code=404, detail={"message": "No route has been solved for this tanker yet."})
    return route


@app.post("/api/dispatch/stops/{stop_id}/delivered")
def stop_delivered(stop_id: str, payload: DeliveredRequest = Body(default=DeliveredRequest()), role: str = Depends(current_role)) -> dict[str, Any]:
    if role == "crew" and not stop_id.startswith("T01-"):
        raise HTTPException(status_code=403, detail={"message": "Crew may complete only assigned T01 stops."})
    try:
        result = services.mark_delivered(stop_id, role)
        if payload.note:
            result["note"] = payload.note[:200]
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc


@app.get("/api/kpis")
def get_kpis(role: str = Depends(current_role)) -> dict[str, Any]:
    return services.kpis()


@app.get("/api/audit")
def audit(role: str = Depends(require_admin)) -> list[dict[str, Any]]:
    return services.STATE["audit"]


@app.get("/api/model/metrics")
def model_metrics(role: str = Depends(current_role)) -> dict[str, Any]:
    return {"model": "Synthetic formula", "r2": None, "mae": None, "training_rows": 0, "test_rows": 0,
            "note": "This reconstruction uses transparent deterministic formulas; no trained ML model is claimed.", "synthetic": True}


@app.post("/api/copilot/chat")
def copilot_chat(payload: ChatRequest, role: str = Depends(current_role)):
    answer = services.copilot_reply(payload.message)
    if not payload.stream:
        return {"response": answer, "role": "assistant", "synthetic": True}

    def event_stream():
        words = answer.split(" ")
        for word in words:
            yield f"data: {json.dumps({'text': word + ' '})}\n\n"
        yield f"data: {json.dumps({'done': True, 'synthetic': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


app.mount("/static", StaticFiles(directory=STATIC, check_dir=False), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html", media_type="text/html")
