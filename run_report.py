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



def main():

    """Main function to orchestrate the interactive reporting session."""

    while True: # Main loop for selecting properties

        # 1. Select Property

        selected_property_info = get_selected_property() # Now returns dict

        if not selected_property_info:

            break # Exit if no property is selected or found



        while True: # Nested loop for running reports on the selected property

            # 2. Discover and Select Report

            available_reports = get_available_reports()

            if not available_reports:

                print("No reports found in the 'reports' directory.")

                break # Go back to property selection

            selected_report = get_selected_report(available_reports)

            

            # 3. Run the selected report

            report_data = run_dynamic_report(selected_report['module'], selected_property_info['property_id']) # Pass only ID to report module

            if not report_data:

                print("Report generation failed.")

                # Ask user what to do next even if report fails

            else:

                # 4. Select Output Format and process the data

                output_function = get_selected_output_format()

                # Pass both report_data and selected_property_info to the output function

                output_function(report_data, selected_property_info) 



            # 5. Ask user what to do next

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


