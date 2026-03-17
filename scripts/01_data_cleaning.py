"""
Phase 1: Shear Line Detection Model (Multi-Province)
Study Area: Bicol Region (NASA POWER Data)
Temporal Resolution: Daily
Period: 2020–2022
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

INPUT_FOLDER = "."  

# Output folders 
OUTPUT_FOLDER = "outputs"
DAILY_FOLDER = os.path.join(OUTPUT_FOLDER, "daily")
YEARLY_FOLDER = os.path.join(OUTPUT_FOLDER, "yearly")

os.makedirs(DAILY_FOLDER, exist_ok=True)
os.makedirs(YEARLY_FOLDER, exist_ok=True)

# NASA POWER missing value
MISSING_FLAG = -999

# Thresholds
RAIN_THRESHOLD_MM = 25
RH_THRESHOLD = 85
WD_MIN_DEG = 30
WD_MAX_DEG = 90
DELTA_T_MAX_C = 7
WS_MAX_MS = 10



def find_header_row(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if line.strip().upper().startswith("YEAR"):
                return i
    raise ValueError(f"Could not find YEAR header in {file_path}")



def classify_shear_line(sli):
    if sli >= 4:
        return "Shear Line Day"
    elif sli == 3:
        return "Possible Shear Line"
    else:
        return "Non-Shear Line Day"



all_yearly_summaries = []

csv_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".csv")]

if not csv_files:
    raise FileNotFoundError("No CSV files found in the input folder.")

print("Detected CSV files:", csv_files)

for file_name in csv_files:
    file_path = os.path.join(INPUT_FOLDER, file_name)
    province_name = os.path.splitext(file_name)[0]  # filename without .csv

    print(f"\nProcessing {province_name}...")


    header_row = find_header_row(file_path)
    df = pd.read_csv(file_path, skiprows=header_row)


    df.columns = df.columns.str.strip().str.upper()

 
    required_cols = ["YEAR", "DOY", "RH2M", "PRECTOTCORR", "WD2M", "T2M_MAX", "T2M_MIN", "WS2M"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"{file_name} is missing required column: {col}")


    df["DATE"] = df.apply(
        lambda row: datetime(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1),
        axis=1
    )
    df["DATE"] = pd.to_datetime(df["DATE"])


    df = df.replace(MISSING_FLAG, np.nan)


    df = df.dropna(subset=["RH2M", "PRECTOTCORR", "WD2M", "T2M_MAX", "T2M_MIN", "WS2M"])

    df = df.sort_values("DATE").reset_index(drop=True)


    df["DELTA_T"] = df["T2M_MAX"] - df["T2M_MIN"]


    df["I1_RAIN"] = (df["PRECTOTCORR"] >= RAIN_THRESHOLD_MM).astype(int)
    df["I2_HUMIDITY"] = (df["RH2M"] >= RH_THRESHOLD).astype(int)
    df["I3_WIND_DIR"] = ((df["WD2M"] >= WD_MIN_DEG) & (df["WD2M"] <= WD_MAX_DEG)).astype(int)
    df["I4_TEMP_RANGE"] = (df["DELTA_T"] <= DELTA_T_MAX_C).astype(int)
    df["I5_WIND_SPEED"] = (df["WS2M"] <= WS_MAX_MS).astype(int)


    df["SLI"] = (
        df["I1_RAIN"] +
        df["I2_HUMIDITY"] +
        df["I3_WIND_DIR"] +
        df["I4_TEMP_RANGE"] +
        df["I5_WIND_SPEED"]
    )

 
    df["CLASSIFICATION"] = df["SLI"].apply(classify_shear_line)


    output_columns = [
        "DATE",
        "PRECTOTCORR", "RH2M", "WD2M", "WS2M",
        "T2M_MAX", "T2M_MIN", "DELTA_T",
        "I1_RAIN", "I2_HUMIDITY", "I3_WIND_DIR", "I4_TEMP_RANGE", "I5_WIND_SPEED",
        "SLI", "CLASSIFICATION"
    ]

    daily_output_file = os.path.join(DAILY_FOLDER, f"{province_name}_daily_shearline.csv")
    df[output_columns].to_csv(daily_output_file, index=False)
    print(f"Daily saved: {daily_output_file}")


    df["YEAR_ONLY"] = df["DATE"].dt.year
    yearly_summary = (
        df[df["CLASSIFICATION"] == "Shear Line Day"]
        .groupby("YEAR_ONLY")
        .size()
        .reset_index(name="Shear_Line_Days")
    )

    yearly_summary["PROVINCE"] = province_name.replace("_", " ").title()

    yearly_output_file = os.path.join(YEARLY_FOLDER, f"{province_name}_yearly_summary.csv")
    yearly_summary.to_csv(yearly_output_file, index=False)
    print(f"Yearly saved: {yearly_output_file}")

    all_yearly_summaries.append(yearly_summary)


# COMBINED REGIONAL SUMMARY
regional_summary = pd.concat(all_yearly_summaries, ignore_index=True)
regional_summary = regional_summary.sort_values(["PROVINCE", "YEAR_ONLY"])

regional_output_file = os.path.join(OUTPUT_FOLDER, "bicol_shearline_yearly_summary.csv")
regional_summary.to_csv(regional_output_file, index=False)

print("\n✅ Phase 1 processing complete.")
print(f"Regional summary saved: {regional_output_file}")
