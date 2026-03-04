import os
import glob
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "lagged_datasets")
OUT_DIR = os.path.join(BASE_DIR, "Tplus_datasets")
os.makedirs(OUT_DIR, exist_ok=True)

files = glob.glob(os.path.join(DATA_DIR, "*_lagged_shearline.csv"))

if not files:
    raise FileNotFoundError("No lagged datasets found.")

print("\nAdding T+1 T+2 T+3 targets...\n")

def add_future(df, k):
    df[f"RAIN_T{k}"] = df["PRECTOTCORR"].shift(-k)
    df[f"RH_T{k}"] = df["RH2M"].shift(-k)
    df[f"WS_T{k}"] = df["WS2M"].shift(-k)
    df[f"WD_T{k}"] = df["WD2M"].shift(-k)
    df[f"DELTA_T_T{k}"] = df["DELTA_T"].shift(-k)
    return df

for path in files:
    name = os.path.basename(path)

    df = pd.read_csv(path)

    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE").reset_index(drop=True)

    for k in [1,2,3]:
        df = add_future(df, k)

    # remove rows without future info
    required = []
    for k in [1,2,3]:
        required += [
            f"RAIN_T{k}",
            f"RH_T{k}",
            f"WS_T{k}",
            f"WD_T{k}",
            f"DELTA_T_T{k}"
        ]

    df = df.dropna(subset=required)

    out_path = os.path.join(
        OUT_DIR,
        name.replace("_lagged_shearline.csv", "_Tplus.csv")
    )

    df.to_csv(out_path, index=False)

    print(f"✅ Saved {os.path.basename(out_path)} | rows={len(df)}")

print("\n✅ DONE — Tplus datasets ready.")