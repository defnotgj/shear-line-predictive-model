import os
import re
import glob
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# If script is inside Tplus_datasets
if os.path.isdir(os.path.join(BASE_DIR, "composite_averages")):
    ROOT_DIR = BASE_DIR
else:
    ROOT_DIR = os.path.join(BASE_DIR, "Tplus_datasets")

CSV_DIR = os.path.join(ROOT_DIR, "composite_averages")
OUT_BASE = os.path.join(ROOT_DIR, "synoptic_maps_Tplus")
os.makedirs(OUT_BASE, exist_ok=True)

print("ROOT_DIR:", ROOT_DIR)
print("CSV_DIR:", CSV_DIR)
print("OUT_BASE:", OUT_BASE)

geojson_files = glob.glob(os.path.join(ROOT_DIR, "*.json")) # FIND GEOJSON
if not geojson_files:
    raise FileNotFoundError(f"No GeoJSON (*.json) found in: {ROOT_DIR}")

GEOJSON_PATH = None
for g in geojson_files:
    nm = os.path.basename(g).lower()
    if "bicol" in nm or "provdist" in nm:
        GEOJSON_PATH = g
        break
if GEOJSON_PATH is None:
    GEOJSON_PATH = geojson_files[0]

print("Using GeoJSON:", os.path.basename(GEOJSON_PATH))
gdf = gpd.read_file(GEOJSON_PATH)

province_column = None
for col in ["adm2_en", "NAME_2", "province", "name", "ADM2_EN"]:
    if col in gdf.columns:
        province_column = col
        break
if province_column is None:
    raise ValueError(f"Could not find province column. GeoJSON columns: {list(gdf.columns)}")

print("GeoJSON province column:", province_column)

BICOL_PROVINCES = [
    "ALBAY",
    "CAMARINES NORTE",
    "CAMARINES SUR",
    "CATANDUANES",
    "MASBATE",
    "SORSOGON",
]

def normalize_province_name(x: str) -> str:
    s = str(x).upper().strip()

    s = re.sub(r"\.CSV$", "", s)
   
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
   
    s = s.replace(" DAILY SHEARLINE TPLUS", "")
    s = s.replace(" DAILY SHEARLINE TPLUS123", "")
    s = s.replace(" DAILY SHEARLINE", "")
    s = s.replace(" TPLUS123", "")
    s = s.replace(" TPLUS", "")

    s = re.sub(r"\s+", " ", s).strip()

    
    s = s.replace("SOORSOGON", "SORSOGON")
    s = s.replace("CCAMARINES SUR", "CAMARINES SUR")
    s = s.replace("CCAMARINES NORTE", "CAMARINES NORTE")

    
    for prov in BICOL_PROVINCES:
        if prov in s:
            return prov

    return s

gdf["PROV_KEY"] = gdf[province_column].apply(normalize_province_name)

def make_maps_for_horizon(csv_path: str, label: str):
    if not os.path.exists(csv_path):
        print(f"Skipping {label} — missing CSV: {csv_path}")
        return

    out_dir = os.path.join(OUT_BASE, label)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n=== {label} ===")
    df = pd.read_csv(csv_path)

    # detect province column in CSV
    csv_prov_col = None
    for candidate in ["PROVINCE", "Province", "province"]:
        if candidate in df.columns:
            csv_prov_col = candidate
            break
    if csv_prov_col is None:
        csv_prov_col = df.columns[0]

    df["PROV_KEY"] = df[csv_prov_col].apply(normalize_province_name)

    # debug mismatches
    geo_set = set(gdf["PROV_KEY"].unique())
    csv_set = set(df["PROV_KEY"].unique())
    miss_csv = sorted(list(geo_set - csv_set))
    miss_geo = sorted(list(csv_set - geo_set))
    if miss_csv:
        print("⚠️ In GeoJSON not in CSV:", miss_csv)
    if miss_geo:
        print("⚠️ In CSV not in GeoJSON:", miss_geo)

    merged = gdf.merge(df, on="PROV_KEY", how="left")

    variables = [
        ("RAIN", "Rainfall (mm)"),
        ("RH", "Relative Humidity (%)"),
        ("WS", "Wind Speed (m/s)"),
        ("WD", "Wind Direction (deg)"),
        ("DELTA_T", "Temperature Range (°C)"),
    ]

    def pick_col(prefix):
        mean_cols = [c for c in merged.columns if c.upper().startswith(prefix) and "MEAN" in c.upper()]
        if mean_cols:
            return mean_cols[0]
        any_cols = [c for c in merged.columns if prefix in c.upper() and c != "PROV_KEY"]
        return any_cols[0] if any_cols else None

    for var, title in variables:
        col = pick_col(var)
        if col is None:
            print(f"Skipping {label} {var}: no column found.")
            continue

        fig, ax = plt.subplots(figsize=(8, 8))
        merged.boundary.plot(ax=ax, linewidth=1, color="black")

        if merged[col].notna().any():
            merged.plot(column=col, legend=True, ax=ax)
        else:
            print(f"⚠️ {label} {var}: still all NaN after merge.")

        ax.set_title(f"{title} — {label}", fontsize=12)
        ax.axis("off")

        out_path = os.path.join(out_dir, f"{var}_{label}.png")
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        print("Saved:", out_path)

make_maps_for_horizon(os.path.join(CSV_DIR, "PROVINCE_composite_T1.csv"), "T+1")
make_maps_for_horizon(os.path.join(CSV_DIR, "PROVINCE_composite_T2.csv"), "T+2")
make_maps_for_horizon(os.path.join(CSV_DIR, "PROVINCE_composite_T3.csv"), "T+3")

print("\n✅ DONE. Check:", OUT_BASE)