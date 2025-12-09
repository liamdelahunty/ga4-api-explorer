from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from google.analytics.admin_v1alpha.types import ListPropertiesRequest
import ga4_client
import sys

def get_selected_property_id():
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
                "property_id": prop.name.split('/')[-1] # Extract just the ID
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

def run_sample_report(property_id):
    """Runs a sample report (top 5 cities by active users) for the given property ID."""
    data_client = ga4_client.get_data_client()
    if not data_client:
        return

    print(f"\nRunning sample report for property ID: {property_id}")

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        limit=5,
        order_bys=[{"metric": {"metric_name": "activeUsers"}, "desc": True}],
    )

    response = data_client.run_report(request)

    print("Report result (Top 5 Cities by Active Users in Last 7 Days):")
    if not response.rows:
        print("No data found for this report.")
        return

    for row in response.rows:
        city = row.dimension_values[0].value
        active_users = row.metric_values[0].value
        print(f"  City: {city}, Active Users: {active_users}")


def main():
    # In the future, this is where we'd add argparse for command-line flags.
    # For now, we'll use the interactive selection.
    selected_property_id = get_selected_property_id()
    if selected_property_id:
        run_sample_report(selected_property_id)


if __name__ == "__main__":
    main()
