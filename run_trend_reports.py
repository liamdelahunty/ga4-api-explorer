#!/usr/bin/env python3
"""
Runs historical trend reports for the last 13 complete calendar months across all GA4 properties listed in properties.json.
"""
import argparse
import datetime
import json
import os
import sys
from dateutil.relativedelta import relativedelta

# Add root folder to sys.path to ensure local imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import ga4_client
from run_report import run_dynamic_report, get_selected_output_format

DEFAULT_TREND_REPORTS = [
    "monthly_acquisition_trend_report",
    "channel_trend_report",
    "monthly_traffic_source_report",
    "device_type_historical_report"
]

def load_properties(config_path="config/properties.json"):
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("properties", [])
    except Exception as e:
        print(f"Error loading properties config: {e}")
        return []

def get_last_13_months_dates():
    today = datetime.date.today()
    # First day of the current month
    first_day_current = today.replace(day=1)
    # Last day of the previous complete calendar month
    last_day_prev = first_day_current - datetime.timedelta(days=1)
    # First day of the month 12 months before the last month (making 13 months total)
    first_day_start = last_day_prev.replace(day=1) - relativedelta(months=12)
    
    return first_day_start.strftime('%Y-%m-%d'), last_day_prev.strftime('%Y-%m-%d')

def main():
    parser = argparse.ArgumentParser(description="Run longitudinal trend reports for the last 13 complete months across GA4 properties.")
    parser.add_argument("-p", "--property-id", help="Filter and run for a single GA4 property ID.")
    parser.add_argument("-o", "--output-format", default="html", choices=["console", "txt", "csv", "html", "csv_html"],
                        help="Output format (default: html).")
    parser.add_argument("--no-cache", action="store_true", help="Bypass response caching.")
    parser.add_argument("--reports", help="Comma-separated list of report module names to run instead of the default trends list.")
    
    args = parser.parse_args()
    
    # Calculate dates
    start_date, end_date = get_last_13_months_dates()
    verbose_date_range_str = f"{start_date} to {end_date}"
    print(f"Reporting period: {verbose_date_range_str} (Last 13 Complete Calendar Months)")
    
    # Load properties
    properties = load_properties()
    if not properties:
        print("No properties found to process. Exiting.")
        return
        
    if args.property_id:
        properties = [p for p in properties if p.get("property_id") == args.property_id]
        if not properties:
            print(f"Error: Property ID '{args.property_id}' not found in configuration.")
            return

    # Choose report modules to run
    report_modules = DEFAULT_TREND_REPORTS
    if args.reports:
        report_modules = [r.strip() for r in args.reports.split(",")]
        
    print(f"Loaded {len(properties)} properties and scheduled {len(report_modules)} trend reports per property.")
    
    google_auth = ga4_client.get_google_auth()
    if not google_auth:
        print("Error: Could not authenticate with Google GA4 API. Check client_secret.json.")
        return

    ran_successfully = 0

    # Run trend reports for each property
    for prop in properties:
        p_name = prop.get("name")
        p_id = prop.get("property_id")
        
        selected_property_info = {
            "display_name": p_name,
            "property_id": p_id
        }
        
        print(f"\n======================================================================")
        print(f"Processing Property: {p_name} ({p_id})")
        print(f"======================================================================")
        
        for module_name in report_modules:
            try:
                # Get the output function from run_report
                output_function, _ = get_selected_output_format(args.output_format, module_name)
                
                report_data = run_dynamic_report(
                    module_name, 
                    p_id, 
                    start_date, 
                    end_date, 
                    google_auth, 
                    no_cache=args.no_cache
                )
                
                if report_data:
                    report_data['date_range'] = verbose_date_range_str
                    output_function(report_data, selected_property_info, start_date, end_date)
                    ran_successfully += 1
                else:
                    print(f"[-] Failed to retrieve data for {module_name}")
            except Exception as e:
                print(f"[-] Error running {module_name} for {p_name}: {e}")

    print(f"\nCompleted! Generated {ran_successfully} trend reports.")

if __name__ == "__main__":
    main()
