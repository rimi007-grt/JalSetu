"""Synthetic Faridabad-shaped demo data. Not official boundaries or live operations."""

WARD_SPECS = [
    {"id": "W01", "name": "NIT 01", "area_km2": 2.56, "slope_pct": 1.91, "impervious_pct": 54.2, "soil_class": "loam", "population": 30621, "water_stress": 65.7, "elevation_m": 186.0},
    {"id": "W02", "name": "Greenfield 04", "area_km2": 1.72, "slope_pct": 1.49, "impervious_pct": 81.4, "soil_class": "loam", "population": 57796, "water_stress": 87.9, "elevation_m": 185.4},
    {"id": "W03", "name": "Greenfield 19", "area_km2": 2.10, "slope_pct": 1.27, "impervious_pct": 76.8, "soil_class": "clay-loam", "population": 41820, "water_stress": 98.0, "elevation_m": 184.9},
    {"id": "W04", "name": "Old Faridabad", "area_km2": 2.35, "slope_pct": 1.63, "impervious_pct": 73.5, "soil_class": "loam", "population": 49210, "water_stress": 78.4, "elevation_m": 186.2},
    {"id": "W05", "name": "Badkhal", "area_km2": 2.40, "slope_pct": 2.18, "impervious_pct": 59.8, "soil_class": "sandy-loam", "population": 28450, "water_stress": 70.3, "elevation_m": 189.0},
    {"id": "W06", "name": "NIT 02", "area_km2": 2.20, "slope_pct": 1.86, "impervious_pct": 68.4, "soil_class": "loam", "population": 36150, "water_stress": 72.6, "elevation_m": 187.2},
    {"id": "W07", "name": "Surajkund Edge", "area_km2": 1.95, "slope_pct": 2.42, "impervious_pct": 48.2, "soil_class": "sandy-loam", "population": 22190, "water_stress": 60.2, "elevation_m": 192.1},
    {"id": "W08", "name": "Sector 15", "area_km2": 2.45, "slope_pct": 1.42, "impervious_pct": 71.1, "soil_class": "loam", "population": 39770, "water_stress": 74.1, "elevation_m": 186.6},
    {"id": "W09", "name": "NIT 03", "area_km2": 2.25, "slope_pct": 1.72, "impervious_pct": 62.9, "soil_class": "clay-loam", "population": 33540, "water_stress": 69.8, "elevation_m": 187.6},
    {"id": "W10", "name": "Sector 21", "area_km2": 2.10, "slope_pct": 1.25, "impervious_pct": 78.8, "soil_class": "loam", "population": 45860, "water_stress": 82.6, "elevation_m": 185.1},
    {"id": "W11", "name": "Greenfield 08", "area_km2": 2.30, "slope_pct": 1.36, "impervious_pct": 74.3, "soil_class": "loam", "population": 40520, "water_stress": 80.7, "elevation_m": 184.8},
    {"id": "W12", "name": "Old Industrial", "area_km2": 2.05, "slope_pct": 1.88, "impervious_pct": 83.1, "soil_class": "clay-loam", "population": 36520, "water_stress": 86.1, "elevation_m": 185.8},
    {"id": "W13", "name": "Sector 28", "area_km2": 1.80, "slope_pct": 1.54, "impervious_pct": 65.5, "soil_class": "loam", "population": 27030, "water_stress": 66.9, "elevation_m": 187.0},
    {"id": "W14", "name": "NIT 04", "area_km2": 2.40, "slope_pct": 1.95, "impervious_pct": 69.7, "soil_class": "loam", "population": 35410, "water_stress": 76.2, "elevation_m": 186.4},
    {"id": "W15", "name": "Sector 30", "area_km2": 2.60, "slope_pct": 1.19, "impervious_pct": 77.4, "soil_class": "clay-loam", "population": 42680, "water_stress": 79.9, "elevation_m": 184.7},
    {"id": "W16", "name": "Neelam", "area_km2": 1.95, "slope_pct": 1.76, "impervious_pct": 72.1, "soil_class": "loam", "population": 31580, "water_stress": 75.4, "elevation_m": 186.0},
    {"id": "W17", "name": "Greenfield 12", "area_km2": 2.20, "slope_pct": 1.33, "impervious_pct": 79.2, "soil_class": "clay-loam", "population": 44730, "water_stress": 85.6, "elevation_m": 184.5},
    {"id": "W18", "name": "NIT 05", "area_km2": 2.15, "slope_pct": 1.97, "impervious_pct": 64.7, "soil_class": "loam", "population": 30280, "water_stress": 68.8, "elevation_m": 187.4},
    {"id": "W19", "name": "Sector 37", "area_km2": 2.05, "slope_pct": 1.58, "impervious_pct": 70.2, "soil_class": "loam", "population": 33890, "water_stress": 73.7, "elevation_m": 186.3},
    {"id": "W20", "name": "Greater Faridabad", "area_km2": 2.30, "slope_pct": 1.22, "impervious_pct": 75.6, "soil_class": "clay-loam", "population": 41860, "water_stress": 81.2, "elevation_m": 184.9},
]

# 25 sites; capacities sum to 22.14 million synthetic liters.
RECHARGE_SITE_SPECS = []
for i in range(25):
    row, col = divmod(i, 5)
    RECHARGE_SITE_SPECS.append({
        "id": f"R{i + 1:02d}",
        "ward_id": f"W{((i * 3) % 20) + 1:02d}",
        "name": f"{'Recharge site' if i % 4 else 'Drain outfall'} {i + 1:02d}",
        "type": "recharge" if i % 4 else "outfall",
        "lat": 28.384 + row * 0.0102 + ((i % 3) * 0.0011),
        "lon": 77.272 + col * 0.0127 + ((i % 2) * 0.0014),
        "capacity_liters": 809_600 + (i % 5) * 38_000,
        "piezometric_decline_m": round(1.2 + (i * 0.17) % 2.6, 2),
        "infiltration_lph": 12_000 + (i * 1_740) % 18_000,
        "score": round(0.57 + ((i * 13) % 39) / 100, 2),
    })

DEPOTS = [
    {"id": "DEP-01", "name": "NIT Depot", "lat": 28.405, "lon": 77.286},
    {"id": "DEP-02", "name": "Greenfield Depot", "lat": 28.396, "lon": 77.319},
]

TANKERS = [
    {"id": f"T{i:02d}", "capacity_liters": 12_000 if i == 1 else 10_000 + (i % 3) * 2_000,
     "available": True, "depot_id": "DEP-01" if i <= 6 else "DEP-02",
     "lat": 28.404 + ((i * 7) % 9) * 0.0012, "lon": 77.285 + ((i * 5) % 10) * 0.0017,
     "crew_id": "demo-crew" if i == 1 else f"crew-{i:02d}"}
    for i in range(1, 13)
]
