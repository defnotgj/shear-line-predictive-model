import os
import glob
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "01_original_data")
OUT_DIR = os.path.join(BASE_DIR, "lagged_datasets")
os.makedirs(OUT_DIR, exist_ok=True)

files = glob.glob(os.path.join(DATA_DIR, "*_daily_shearline.csv"))
if not files:
    raise FileNotFoundError("No *_daily_shearline.csv found inside 01_original_data")

print("\nFound datasets:")
for f in files:
    print(" -", os.path.basename(f))

def add_lags(df, col, lags=(1,2,3)):
    for k in lags:
        df[f"{col}_L{k}"] = df[col].shift(k)
    return df

print("\nCreating lag features (L1–L3) + WD sin/cos + filtering shear line days...\n")

for path in files:
    name = os.path.basename(path)
    df = pd.read_csv(path)

    # Clean -999 or other placeholders
    df = df.replace(-999, pd.NA)

    # Parse and sort dates
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    df = df.dropna(subset=["DATE"])
    df = df.sort_values("DATE").reset_index(drop=True)

    # ---- Wind direction fix ----
    # Convert WD2M into sin/cos (handles circular nature)
    df["WD_SIN"] = np.sin(np.deg2rad(df["WD2M"]))
    df["WD_COS"] = np.cos(np.deg2rad(df["WD2M"]))

    # ---- Lag all base predictors ----
    lag_list = (1, 2, 3)

    for base in ["PRECTOTCORR", "RH2M", "WS2M", "DELTA_T", "WD_SIN", "WD_COS"]:
        df = add_lags(df, base, lags=lag_list)

    # Drop rows that don’t have lag history
    needed_lags = []
    for base in ["PRECTOTCORR", "RH2M", "WS2M", "DELTA_T", "WD_SIN", "WD_COS"]:
        for k in lag_list:
            needed_lags.append(f"{base}_L{k}")

    df = df.dropna(subset=needed_lags)

    # ---- Keep only shear line days (Day 0 rows) ----
    if "CLASSIFICATION" not in df.columns:
        print(f"❌ Skipping {name}: missing CLASSIFICATION column")
        continue

    shear = df[df["CLASSIFICATION"].astype(str).str.strip().str.lower() == "shear line day"].copy()

    out_path = os.path.join(OUT_DIR, name.replace(".csv", "_lagged_shearline.csv"))
    shear.to_csv(out_path, index=False)

    print(f"✅ Saved {os.path.basename(out_path)} | rows kept: {len(shear)}")

print("\n✅ DONE — Lagged shear line datasets created in:", OUT_DIR)