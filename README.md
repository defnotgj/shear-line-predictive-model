# Predictive Modeling of Post-Shear Line Atmospheric Responses

This project analyzes atmospheric responses following shear line events in the Bicol Region using statistical modeling.

---

## Study Overview
This research develops a statistical predictive model to analyze atmospheric changes following confirmed shear line events in the Bicol Region using short-term forecast horizons (T+1, T+2, T+3).

---

## Data Source
NASA POWER meteorological database (2020–2022)

Variables used:
- Precipitation (PRECTOTCORR)
- Relative Humidity (RH2M)
- Wind Speed (WS2M)
- Wind Direction (WD2M)
- Maximum Temperature (Tmax)
- Minimum Temperature (Tmin)

Total filtered observations: **1,616**

---

## Methodology

1. Data preprocessing and shear line filtering  
2. Feature construction (Temperature Range ΔT)  
3. Forecast horizon construction (T+1, T+2, T+3)  
4. Multiple Linear Regression (OLS)  
5. Model evaluation using R² and RMSE  

---

## Repository Structure
