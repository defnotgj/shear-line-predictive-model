import os
import glob
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Tplus_datasets")

files = glob.glob(os.path.join(DATA_DIR, "*_Tplus.csv"))

if not files:
    raise FileNotFoundError("No Tplus datasets found.")

df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

print("Total rows:", len(df))

# ----------------------------
# FEATURES (predictors)
# ----------------------------
FEATURES = [
    "PRECTOTCORR",
    "RH2M",
    "WS2M",
    "WD2M",
    "DELTA_T"
]

# add lag features automatically if present
FEATURES += [c for c in df.columns if "_L" in c]

VARIABLES = ["RAIN","RH","WS","WD","DELTA_T"]
HORIZONS = [1,2,3]

print("\n==============================")
print("T+1 vs T+2 vs T+3 COMPARISON")
print("==============================")

for var in VARIABLES:

    print(f"\n--- {var} ---")

    for k in HORIZONS:

        target = f"{var}_T{k}" if var != "DELTA_T" else f"DELTA_T_T{k}"

        data = df.dropna(subset=FEATURES + [target])

        if len(data) < 30:
            print(f"{target}: not enough rows")
            continue

        X = data[FEATURES]
        y = data[target]

        model = LinearRegression()
        model.fit(X, y)

        pred = model.predict(X)

        rmse = mean_squared_error(y, pred) ** 0.5
        r2 = r2_score(y, pred)

        print(f"{target}: Rows={len(data)} | RMSE={rmse:.3f} | R²={r2:.3f}")