import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure the project root is available for the local ASGI/service modules.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import services
from main import app


# Public demo-role selectors used by the endpoint contract checks.
ADMIN = {"Authorization": "Bearer demo-admin"}
CREW = {"Authorization": "Bearer demo-crew"}


class JalSetuApiTests(unittest.TestCase):
    def setUp(self):
        services.STATE.update({"rain_mm": 95.0, "duration_hours": 6, "allocated_liters": 0, "allocated_by_site": {}, "routes": {}, "delivered": set(), "audit": []})
        self.client = TestClient(app)

    def test_health_and_manifest_are_public_and_exact(self):
        self.assertEqual(self.client.get("/_jalsetu/health").status_code, 200)
        response = self.client.get("/manus-routes.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["routes"][0]["path"], "/")

    def test_wards_are_synthetic_geojson_and_require_demo_role(self):
        self.assertEqual(self.client.get("/api/wards").status_code, 401)
        response = self.client.get("/api/wards", headers=ADMIN)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["type"], "FeatureCollection")
        self.assertEqual(len(response.json()["features"]), 20)
        self.assertEqual(response.json()["features"][0]["properties"]["id"], "W01")

    def test_crew_is_limited_to_assigned_vehicle_and_cannot_administer(self):
        payload = self.client.get("/api/tankers", headers=CREW).json()
        self.assertEqual([t["id"] for t in payload["tankers"]], ["T01"])
        self.assertEqual(self.client.post("/api/dispatch/solve", headers=CREW).status_code, 403)
        self.assertEqual(self.client.post("/api/simulate", headers=CREW, json={"rain_mm": 120, "duration_hours": 3}).status_code, 403)
        self.client.post("/api/dispatch/solve", headers=ADMIN)
        admin_routes = self.client.get("/api/dispatch/routes", headers=ADMIN).json()
        crew_routes = self.client.get("/api/dispatch/routes", headers=CREW).json()
        self.assertEqual(admin_routes["total_routes"], 12)
        self.assertEqual([route["tanker_id"] for route in crew_routes["routes"]], ["T01"])
        self.assertEqual(self.client.get("/api/dispatch/routes/T02", headers=CREW).status_code, 403)
        stop_id = crew_routes["routes"][0]["stops"][0]["stop_id"]
        delivered = self.client.post(f"/api/dispatch/stops/{stop_id}/delivered", headers=CREW, json={"note": "Demo completion"})
        self.assertEqual(delivered.status_code, 200)
        refreshed = self.client.get("/api/dispatch/routes/T01", headers=CREW).json()
        self.assertTrue(next(stop for stop in refreshed["stops"] if stop["stop_id"] == stop_id)["delivered"])
        metrics = self.client.get("/api/kpis", headers=CREW).json()
        self.assertEqual((metrics["delivered_stops"], metrics["total_stops"]), (1, 20))
        self.assertEqual(metrics["delivery_completion_pct"], 5.0)

    def test_admin_can_apply_scenario_and_simulate_recharge(self):
        scenario = self.client.post("/api/simulate", headers=ADMIN, json={"rain_mm": 120, "duration_hours": 3})
        self.assertEqual(scenario.status_code, 200)
        self.assertEqual(scenario.json()["rain_mm"], 120)
        self.assertGreater(scenario.json()["runoff_liters"], 0)
        captured_before = self.client.get("/api/kpis", headers=ADMIN).json()["recharge_liters"]
        allocation = self.client.post("/api/recharge/allocate", headers=ADMIN, json={"site_id": "R01", "liters": 250000})
        self.assertEqual(allocation.status_code, 200)
        self.assertEqual(allocation.json()["allocated_liters"], 250000)
        features = self.client.get("/api/recharge/sites", headers=ADMIN).json()["features"]
        per_site = {feature["id"]: feature["properties"]["allocated_liters"] for feature in features}
        self.assertEqual(per_site["R01"], 250000)
        self.assertEqual(per_site["R02"], 0)
        metrics = self.client.get("/api/kpis", headers=ADMIN).json()
        self.assertEqual(metrics["recharge_liters"], captured_before)
        self.assertEqual(metrics["allocated_liters"], 250000)
        self.assertEqual(metrics["total_stops"], 0)
        self.assertEqual(metrics["delivery_completion_pct"], 0.0)

    def test_dispatch_sse_and_demo_copilot(self):
        result = self.client.post("/api/dispatch/solve", headers=ADMIN)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["total_routes"], 12)
        routes = result.json()["routes"]
        stops = [stop for route in routes for stop in route["stops"]]
        self.assertTrue(all(route["stops"] for route in routes))
        self.assertEqual(len(stops), 20)
        self.assertEqual(len({stop["ward_id"] for stop in stops}), 20)
        stream = self.client.post("/api/copilot/chat", headers=ADMIN, json={"message": "How can I reduce flood risk?", "stream": True})
        self.assertEqual(stream.status_code, 200)
        self.assertIn("text/event-stream", stream.headers.get("content-type", ""))
        self.assertIn("synthetic", stream.text.lower())


if __name__ == "__main__":
    unittest.main()
