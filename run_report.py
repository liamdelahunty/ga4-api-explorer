from google.analytics.admin_v1alpha.types import ListPropertiesRequest
import ga4_client
import output_manager # Import our new output manager
import os
import sys
import importlib.util

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

def get_selected_property():
    """Presents an interactive menu to the user to select a GA4 property."""
    admin_client = ga4_client.get_admin_client()
    if not admin_client:
        return None

    accounts = []
    for account in admin_client.list_accounts():
        accounts.append(account)

    if not accounts:
        print("No GA4 accounts found that are accessible by this service account.")
        return None

    properties = {}
    property_list_counter = 1
    
    print("\nAvailable GA4 Properties:")
    for account in accounts:
        request = ListPropertiesRequest(
            filter=f"ancestor:{account.name}"
        )
        for prop in admin_client.list_properties(request=request):
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
        selection = input("Enter the number of the property you want to report on: ")
        if selection in properties:
            selected_property = properties[selection]
            print(f"You selected: {selected_property['display_name']} (ID: {selected_property['property_id']})")
            return selected_property['property_id']
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

def get_selected_output_format():
    """Presents an interactive menu to select the output format."""
    print("\nSelect Output Format:")
    print("1. Print to Console")
    print("2. Save as CSV")
    print("3. Save as HTML")

    output_formats = {
        "1": output_manager.print_to_console,
        "2": output_manager.save_to_csv,
        "3": output_manager.save_to_html
    }

    while True:
        selection = input("Enter the number for the output format: ")
        if selection in output_formats:
            return output_formats[selection]
        else:
            print("Invalid selection. Please enter a valid number.")

def run_dynamic_report(report_module_name, property_id):
    """Dynamically imports and runs a report module."""
    data_client = ga4_client.get_data_client()
    if not data_client:
        return None

    try:
        module_path = f"reports.{report_module_name}"
        report_module = importlib.import_module(module_path)
        print(f"\nRunning '{report_module_name.replace('_', ' ').title()}' report for property ID: {property_id}")
        return report_module.run_report(property_id, data_client)
    except ImportError as e:
        print(f"Error: Could not import report module '{report_module_name}'. {e}")
        return None
    except Exception as e:
        print(f"An error occurred while running the report: {e}")
        return None

def main():
    # 1. Select Property
    selected_property_id = get_selected_property()
    if not selected_property_id:
        return

    # 2. Discover and Select Report
    available_reports = get_available_reports()
    if not available_reports:
        print("No reports found in the 'reports' directory.")
        return
    selected_report = get_selected_report(available_reports)
    
    # 3. Run the selected report
    report_data = run_dynamic_report(selected_report['module'], selected_property_id)
    if not report_data:
        print("Report generation failed.")
        return
        
    # 4. Select Output Format and process the data
    output_function = get_selected_output_format()
    output_function(report_data)


if __name__ == "__main__":
    main()
