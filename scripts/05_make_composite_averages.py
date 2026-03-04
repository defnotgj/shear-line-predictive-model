import os
import glob
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "composite_averages")
os.makedirs(OUT_DIR, exist_ok=True)

files = glob.glob(os.path.join(BASE_DIR, "*_daily_shearline_Tplus.csv"))
if not files:
    raise FileNotFoundError("No *_daily_shearline_Tplus.csv files found in this folder.")


VARS = ["RAIN", "RH", "WS", "WD", "DELTA_T"]
H = [1, 2, 3]

def safe_mean(series: pd.Series):
    """Mean that ignores missing values."""
    return series.dropna().mean()

province_rows_by_h = {1: [], 2: [], 3: []}
regional_frames_by_h = {1: [], 2: [], 3: []}

print("\n==============================")
print("MAKING COMPOSITE AVERAGES")
print("==============================\n")

for path in files:
    fname = os.path.basename(path)
    prov = fname.replace("_post_shearline_Tplus123.csv", "")

    df = pd.read_csv(path)
    df = df.replace(-999, pd.NA)

    for k in H:
        row = {"PROVINCE": prov}

        for var in VARS:
            col = f"{var}_T{k}" if var != "DELTA_T" else f"DELTA_T_T{k}"
            if col not in df.columns:
                row[var] = pd.NA
            else:
                row[var] = safe_mean(df[col])

        province_rows_by_h[k].append(row)
        regional_frames_by_h[k].append(df)

    print(f"✅ Read {prov}: {len(df)} rows")

for k in H:
    out_prov = pd.DataFrame(province_rows_by_h[k])
    out_path = os.path.join(OUT_DIR, f"PROVINCE_composite_T{k}.csv")
    out_prov.to_csv(out_path, index=False)
    print(f"\nSaved: {os.path.basename(out_path)}  (rows={len(out_prov)})")

for k in H:
    combined = pd.concat(regional_frames_by_h[k], ignore_index=True).replace(-999, pd.NA)

    reg_row = {"REGION": "BICOL"}
    for var in VARS:
        col = f"{var}_T{k}" if var != "DELTA_T" else f"DELTA_T_T{k}"
        reg_row[var] = safe_mean(combined[col]) if col in combined.columns else pd.NA

    out_reg = pd.DataFrame([reg_row])
    out_path = os.path.join(OUT_DIR, f"REGIONAL_composite_T{k}.csv")
    out_reg.to_csv(out_path, index=False)
    print(f"Saved: {os.path.basename(out_path)}  (1 row)")

print("\n✅ DONE. Check this folder:")
print(OUT_DIR)