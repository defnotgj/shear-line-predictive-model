import os
import glob
import pandas as pd

# =====================================================
# SETUP PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "phase2_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Find all daily shearline files
pattern = os.path.join(BASE_DIR, "*_daily_shearline.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(
        "No *_daily_shearline.csv files found in this folder."
    )

print("Found files:")
for f in files:
    print(" -", os.path.basename(f))

# =====================================================
# PROCESS EACH PROVINCE
# =====================================================

for fpath in files:
    fname = os.path.basename(fpath)
    prov = fname.replace("_daily_shearline.csv", "")

    print(f"\nProcessing {prov}...")

    df = pd.read_csv(fpath)

    # ===============================
    # ROBUST DATE FIX (WORKS FOR ALL FILES)
    # ===============================
    df["DATE"] = df["DATE"].astype(str).str.strip()

    # Try normal parsing
    d1 = pd.to_datetime(df["DATE"], errors="coerce")

    # Try day-first parsing (for Cam Norte)
    d2 = pd.to_datetime(df["DATE"], errors="coerce", dayfirst=True)

    # Combine successful parses
    df["DATE"] = d1.fillna(d2)

    # Remove rows with invalid dates BEFORE shifting
    bad = df["DATE"].isna().sum()
    if bad > 0:
        print(f"⚠️ {prov}: removed {bad} invalid DATE rows")
        df = df.dropna(subset=["DATE"])

    # Sort chronologically
    df = df.sort_values("DATE").reset_index(drop=True)

    # Save clean ISO date format
    df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")

    # ===============================
    # CREATE NEXT-DAY VARIABLES
    # ===============================
    df["RAIN_T1"] = df["PRECTOTCORR"].shift(-1)
    df["RH_T1"] = df["RH2M"].shift(-1)
    df["WS_T1"] = df["WS2M"].shift(-1)
    df["WD_T1"] = df["WD2M"].shift(-1)
    df["DELTA_T_T1"] = df["DELTA_T"].shift(-1)

    # Keep confirmed shear line days only
    confirmed = df[df["CLASSIFICATION"] == "Shear Line Day"].copy()

    # Remove rows without tomorrow values
    confirmed = confirmed.dropna(
        subset=["RAIN_T1", "RH_T1", "WS_T1", "WD_T1", "DELTA_T_T1"]
    )

    # ===============================
    # SAVE OUTPUT
    # ===============================
    out_path = os.path.join(
        OUTPUT_DIR, f"{prov}_post_shearline_T1.csv"
    )

    confirmed.to_csv(out_path, index=False)

    print(f"✅ {prov}: saved {len(confirmed)} rows")

print("\n✅ Phase 2 Step 1 COMPLETE — all provinces processed.")
