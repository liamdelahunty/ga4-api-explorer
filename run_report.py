from google.analytics.admin_v1alpha.types import ListPropertiesRequest
import ga4_client
import output_manager # Import our new output manager
import os
import sys
import importlib.util
from datetime import datetime, timedelta, date
import json # New import for caching
import hashlib # New import for caching
import time # FIX: Missing import for time.time()
import argparse # New import for command-line arguments


# Cache duration in seconds (e.g., 4 hours)
CACHE_DURATION = 4 * 3600 

def _cleanup_cache():
    """Deletes stale cache files from the cache directory."""
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        return

    current_time = time.time()
    for filename in os.listdir(cache_dir):
        filepath = os.path.join(cache_dir, filename)
        if os.path.isfile(filepath):
            file_mtime = os.path.getmtime(filepath)
            if (current_time - file_mtime) > CACHE_DURATION: # Use CACHE_DURATION for simplicity, could be CLEANUP_THRESHOLD
                try:
                    os.remove(filepath)
                    print(f"Cleaned up stale cache file: {filepath}")
                except Exception as e:
                    print(f"Error cleaning up cache file {filepath}: {e}")

def get_available_reports():
    """Dynamically discovers available reports in the 'reports' directory."""
    reports = {}
    reports_dir = "reports"
    for filename in os.listdir(reports_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            report_name = filename[:-3] # Remove .py extension
            reports[str(len(reports) + 1)] = {
                "name": report_name.replace("_", " ").title(),
                "module": report_name
            }
    return reports

def get_property_info_by_id(property_id_str):
    """Fetches property info by ID using the Admin API."""
    admin_client = ga4_client.get_admin_client()
    if not admin_client:
        return None
    try:
        property_resource = admin_client.get_property(name=f"properties/{property_id_str}")
        return {
            "display_name": property_resource.display_name,
            "property_id": property_id_str
        }
    except Exception as e:
        print(f"Error: Could not find or access property ID '{property_id_str}'. {e}")
        return None

def get_selected_property():

    """Presents a sorted, interactive menu to the user to select a GA4 property.

    Returns a dictionary with 'display_name' and 'property_id' of the selected property.

    """

    admin_client = ga4_client.get_admin_client()

    if not admin_client:

        return None



    # Fetch and sort accounts alphabetically by display name

    all_accounts = list(admin_client.list_accounts())

    all_accounts.sort(key=lambda account: account.display_name)



    if not all_accounts:

        print("No GA4 accounts found that are accessible by this service account.")

        return None



    properties = {}

    property_list_counter = 1

    

    print("\nAvailable GA4 Properties:")

    for account in all_accounts:

        print(f"\n--- Account: {account.display_name} ---")

        

        # Fetch all properties for the account

        request = ListPropertiesRequest(filter=f"ancestor:{account.name}")

        account_properties = list(admin_client.list_properties(request=request))



        # Sort properties: 'www' first, then alphabetically

        def sort_key(prop):

            is_www = prop.display_name.lower().startswith('www')

            return (0, prop.display_name) if is_www else (1, prop.display_name)

        

        account_properties.sort(key=sort_key)



        if not account_properties:

            print("  No properties found for this account.")

            continue



        for prop in account_properties:

            properties[str(property_list_counter)] = {

                "display_name": prop.display_name,

                "property_id": prop.name.split('/')[-1]

            }

            print(f"{property_list_counter}. {prop.display_name} (ID: {prop.name.split('/')[-1]})")

            property_list_counter += 1

    

    if not properties:

        print("No GA4 properties found that are accessible by this service account.")

        return None



    while True:

        selection = input("\nEnter the number of the property you want to report on: ")

        if selection in properties:

            selected_property = properties[selection]

            print(f"You selected: {selected_property['display_name']} (ID: {selected_property['property_id']})")

            return selected_property

        else:

            print("Invalid selection. Please enter a valid number.")


def get_selected_report(reports):
    """Presents an interactive menu to select an available report."""
    print("\nAvailable Reports:")
    for key, report in reports.items():
        print(f"{key}. {report['name']}")
    
    while True:
        selection = input("Enter the number of the report you want to run: ")
        if selection in reports:
            return reports[selection]
        else:
            print("Invalid selection. Please enter a valid number.")

def get_selected_date_range():
    """Presents a menu to select a date range and returns start_date, end_date, a display string, and a verbose date range string."""
    print("\nSelect a Date Range:")
    print("1. Last 7 Days")
    print("2. Last 28 Days")
    print("3. Last 90 Days")
    print("4. Last Calendar Month (Default)")
    print("5. Custom Date Range")

    today = date.today()
    selection = input("Enter your choice (press Enter for default): ")

    if selection == "1":
        start_date = today - timedelta(days=7)
        return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), "Last 7 Days", f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
    elif selection == "2":
        start_date = today - timedelta(days=28)
        return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), "Last 28 Days", f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
    elif selection == "3":
        start_date = today - timedelta(days=90)
        return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), "Last 90 Days", f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
    elif selection == "5":
        while True:
            try:
                start_str = input("Enter start date (YYYY-MM-DD): ")
                end_str = input("Enter end date (YYYY-MM-DD): ")
                datetime.strptime(start_str, '%Y-%m-%d')
                datetime.strptime(end_str, '%Y-%m-%d')
                return start_str, end_str, f"{start_str} to {end_str}", f"{start_str} to {end_str}"
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
    else: # Default to Last Calendar Month
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        start_date = last_day_of_previous_month.replace(day=1)
        return start_date.strftime('%Y-%m-%d'), last_day_of_previous_month.strftime('%Y-%m-%d'), "Last Calendar Month", f"{start_date.strftime('%Y-%m-%d')} to {last_day_of_previous_month.strftime('%Y-%m-%d')}"


def get_selected_output_format():
    """Presents an interactive menu to select the output format."""
    # Define options with their display names and corresponding functions
    output_options_raw = [
        ("Print to Console", output_manager.print_to_console),
        ("Save as CSV", output_manager.save_to_csv),
        ("Save as CSV & HTML", output_manager.save_to_csv_and_html),
        ("Save as HTML", output_manager.save_to_html),
    ]

    # Sort options alphabetically by display name
    output_options_raw.sort(key=lambda x: x[0])

    # Create a numbered menu and a mapping for selection
    output_options_menu = {}
    output_functions_map = {}
    print("\nSelect Output Format:")
    for i, (display_name, func) in enumerate(output_options_raw, 1):
        output_options_menu[str(i)] = display_name
        output_functions_map[str(i)] = func
        print(f"{i}. {display_name}")

    while True:
        selection = input("Enter the number for the output format: ")
        if selection in output_functions_map:
            return output_functions_map[selection]
        else:
            print("Invalid selection. Please enter a valid number.")

def run_dynamic_report(report_module_name, property_id, start_date, end_date):
    """Dynamically imports and runs a report module for a given date range, with caching."""
    
    # Generate cache key
    cache_key_data = {
        "property_id": property_id,
        "report_module": report_module_name,
        "start_date": start_date,
        "end_date": end_date
    }
    cache_key_string = json.dumps(cache_key_data, sort_keys=True)
    cache_filename = hashlib.md5(cache_key_string.encode('utf-8')).hexdigest() + ".json"
    cache_filepath = os.path.join("cache", cache_filename)

    # Check cache
    if os.path.exists(cache_filepath):
        file_mtime = os.path.getmtime(cache_filepath)
        if (time.time() - file_mtime) < CACHE_DURATION:
            print(f"Loading report from cache: {cache_filepath}")
            try:
                with open(cache_filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache file: {e}. Re-running report.")

    # If not in cache or cache is stale, run report
    data_client = ga4_client.get_data_client()
    if not data_client:
        return None

    try:
        module_path = f"reports.{report_module_name}"
        report_module = importlib.import_module(module_path)
        print(f"\nRunning '{report_module_name.replace('_', ' ').title()}' report for property ID: {property_id} (API call)")
        report_data = report_module.run_report(property_id, data_client, start_date, end_date)
        
        # Save to cache if report ran successfully
        if report_data:
            os.makedirs("cache", exist_ok=True)
            with open(cache_filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f)
            print(f"Report saved to cache: {cache_filepath}")
        
        return report_data

    except ImportError as e:
        print(f"Error: Could not import report module '{report_module_name}'. {e}")
        return None
    except Exception as e:
        print(f"An error occurred while running the report: {e}")
        return None

def main():
    """Main function to orchestrate the interactive reporting session."""
    _cleanup_cache() # Clean up stale cache files at the start of each session

    parser = argparse.ArgumentParser(description='Run Google Analytics 4 reports.')
    parser.add_argument('-p', '--property-id', type=str, help='Specify a GA4 property ID to run reports non-interactively.')
    args = parser.parse_args()

    while True: # Main loop for selecting properties
        # 1. Select Property (interactive or via command-line arg)
        selected_property_info = None
        if args.property_id:
            print(f"Attempting to use property ID from command-line: {args.property_id}")
            selected_property_info = get_property_info_by_id(args.property_id)
            if not selected_property_info:
                print("Invalid or inaccessible property ID provided via command-line. Falling back to interactive selection...")
                selected_property_info = get_selected_property()
        else:
            selected_property_info = get_selected_property()

        if not selected_property_info:
            break # Exit if no property is selected or found

        while True: # Nested loop for running reports on the selected property
            # 2. Discover and Select Report
            available_reports = get_available_reports()
            if not available_reports:
                print("No reports found in the 'reports' directory.")
                break # Go back to property selection
            selected_report = get_selected_report(available_reports)
            
            # 3. Select Date Range
            start_date, end_date, friendly_date_range_str, verbose_date_range_str = get_selected_date_range()

            # 4. Run the selected report
            report_data = run_dynamic_report(selected_report['module'], selected_property_info['property_id'], start_date, end_date)
            
            if not report_data:
                print("Report generation failed.")
                # Ask user what to do next even if report fails
            else:
                # Add verbose date range string to report data for output
                report_data['date_range'] = verbose_date_range_str
                # 5. Select Output Format and process the data
                output_function = get_selected_output_format()
                # Pass all necessary info to the output function
                output_function(report_data, selected_property_info, start_date, end_date) 

            # 6. Ask user what to do next
            print("\nWhat would you like to do next?")
            print("(R)un another report for this property")
            print("(C)hange property")
            print("(Q)uit")
            
            while True:
                next_action = input("Enter your choice: ").upper()
                if next_action in ["R", "C", "Q"]:
                    break
                else:
                    print("Invalid choice. Please enter R, C, or Q.")
            
            if next_action == "R":
                continue # Continue the inner loop
            elif next_action == "C":
                break # Break the inner loop to go to property selection
            elif next_action == "Q":
                print("Exiting...")
                return # Exit the entire script
        
        # This part is reached if user chose to change property
        print("\nReturning to property selection...")


if __name__ == "__main__":
    main()
