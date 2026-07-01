#!/usr/bin/env python3
"""
Runs key reports for the last calendar month across all GA4 properties listed in properties.json.
"""
import argparse
import datetime
import json
import os
import sys

# Add root folder to sys.path to ensure local imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import ga4_client
from run_report import run_dynamic_report, get_selected_output_format

DEFAULT_REPORTS = [
    "traffic_acquisition_report",
    "ai_traffic_acquisition_report",
    "top_pages_report",
    "device_type_report",
    "channel_overview_report"
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

def get_last_calendar_month_dates():
    today = datetime.date.today()
    # First day of the current month
    first_day_current = today.replace(day=1)
    # Last day of the previous month
    last_day_prev = first_day_current - datetime.timedelta(days=1)
    # First day of the previous month
    first_day_prev = last_day_prev.replace(day=1)
    
    return first_day_prev.strftime('%Y-%m-%d'), last_day_prev.strftime('%Y-%m-%d')

def main():
    parser = argparse.ArgumentParser(description="Run essential reports for the last calendar month across GA4 properties.")
    parser.add_argument("-p", "--property-id", help="Filter and run for a single GA4 property ID.")
    parser.add_argument("-o", "--output-format", default="html", choices=["console", "txt", "csv", "html", "csv_html"],
                        help="Output format (default: html).")
    parser.add_argument("--no-cache", action="store_true", help="Bypass response caching.")
    parser.add_argument("--reports", help="Comma-separated list of report module names to run instead of the default list.")
    
    args = parser.parse_args()
    
    # Calculate dates
    start_date, end_date = get_last_calendar_month_dates()
    verbose_date_range_str = f"{start_date} to {end_date}"
    print(f"Reporting period: {verbose_date_range_str} (Last Calendar Month)")
    
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
    report_modules = DEFAULT_REPORTS
    if args.reports:
        report_modules = [r.strip() for r in args.reports.split(",")]
        
    print(f"Loaded {len(properties)} properties and scheduled {len(report_modules)} reports per property.")
    
    google_auth = ga4_client.get_google_auth()
    if not google_auth:
        print("Error: Could not authenticate with Google GA4 API. Check client_secret.json.")
        return

    # Keep track of active reports successfully run
    ran_successfully = 0

    # 1. Run individual property reports
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

    # 2. Run All Properties Collation Report once (if not filtered to a single property)
    if not args.property_id:
        print(f"\n======================================================================")
        print(f"Running Aggregated All Properties Collation Report")
        print(f"======================================================================")
        collation_module = "all_properties_ai_traffic_report"
        try:
            output_function, _ = get_selected_output_format(args.output_format, collation_module)
            selected_property_info = {"display_name": "All Properties", "property_id": "all"}
            
            report_data = run_dynamic_report(
                collation_module,
                "all",
                start_date,
                end_date,
                google_auth,
                no_cache=args.no_cache
            )
            if report_data:
                report_data['date_range'] = verbose_date_range_str
                output_function(report_data, selected_property_info, start_date, end_date)
                ran_successfully += 1
        except Exception as e:
            print(f"[-] Error running all properties collation report: {e}")

    print(f"\nCompleted! Generated {ran_successfully} reports.")

if __name__ == "__main__":
    main()
