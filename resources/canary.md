# Canary Monitoring Report

## Overview
The Canary Monitoring Report is a standalone script designed for cross-property performance monitoring. It provides a high-level "early warning" system by comparing recent traffic trends across multiple GA4 properties against historical baselines.

## Features
- **Multi-Property Monitoring:** Analyze dozens of GA4 properties in a single run.
- **Historical Baselines:** Compares the last 7 days of traffic against:
    - **Last Week** (Previous 7-day period)
    - **Last Month** (Same period, previous month)
    - **Last Year** (Same period, previous year)
- **Traffic Light System:** Visual indicators for significant traffic fluctuations.
- **Granular Detail:** Breakdown of top Source/Medium channels for each property.

## Traffic Light Thresholds
The report uses color-coding to highlight performance changes:

| Color | Change | Status |
| :--- | :--- | :--- |
| 🔴 Red | ≤ -25% | Critical Drop |
| 🟠 Amber | -25% to -10% | Warning |
| ⚪ Neutral | -10% to +10% | Stable |
| 🟢 Light Green | +10% to +25% | Moderate Growth |
| ✅ Dark Green | ≥ +25% | Significant Growth |

## Prerequisites
1. **Property Configuration:** Ensure you have a `properties.json` file in the `config/` directory.
    ```json
    [
        {"id": "123456789", "name": "My Website"},
        {"id": "987654321", "name": "My Other Website"}
    ]
    ```
2. **Authentication:** Ensure your environment is authenticated with Google Cloud and has access to the specified Property IDs.

## Usage
Run the script directly from the project root:

```bash
python reports/monitoring/weekly_canary_html.py --config config/properties.json
```

The output is generated as an interactive HTML file, allowing you to quickly scan for performance anomalies across your entire portfolio.

---
*Note: This report is separate from the main `run_report.py` workflow to allow for batch processing and specialized time-period comparisons.*
