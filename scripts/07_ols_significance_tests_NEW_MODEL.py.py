import os
import glob
import pandas as pd
import statsmodels.api as sm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "Tplus_datasets")

files = glob.glob(os.path.join(DATA_DIR, "*_daily_shearline_Tplus.csv"))

if not files:
    raise FileNotFoundError(
        f"No *_daily_shearline_Tplus.csv found in {DATA_DIR}"
    )

print("\nDatasets found:", len(files))

df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
df = df.dropna(subset=["DATE"])

print("Total rows:", len(df))

FEATURES = ["PRECTOTCORR","RH2M","WS2M","WD2M","DELTA_T"]

TARGETS = [
    "RAIN_T1","RAIN_T2","RAIN_T3",
    "RH_T1","RH_T2","RH_T3",
    "WS_T1","WS_T2","WS_T3",
    "WD_T1","WD_T2","WD_T3",
    "DELTA_T_T1","DELTA_T_T2","DELTA_T_T3"
]


print("\n==============================")
print("OLS SIGNIFICANCE TESTS (NEW MODEL)")
print("==============================")

for target in TARGETS:

    data = df.dropna(subset=FEATURES + [target])

    if len(data) < 30:
        print(f"\nSkipping {target}: not enough rows")
        continue

    X = sm.add_constant(data[FEATURES])
    y = data[target]

    model = sm.OLS(y, X).fit()

    print("\n-----------------------------")
    print("TARGET:", target)
    print("-----------------------------")
    print("F-test p-value:", model.f_pvalue)
    print("\nVariable p-values:")
    print(model.pvalues)

print("\n✅ DONE — New model significance testing complete.")