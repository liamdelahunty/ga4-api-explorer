from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient
from google.oauth2 import service_account
import os

def list_properties():
    """Lists GA4 properties accessible by the authenticated service account."""
    # Explicitly load credentials from the service account key file.
    # Make sure your service account JSON file is in the 'config' directory
    # and named 'client_secret.json'.
    
    # Construct the path to the credentials file
    credentials_path = os.path.join(os.path.dirname(__file__), "config", "client_secret.json")

    # Check if the credentials file exists
    if not os.path.exists(credentials_path):
        print(f"Error: Credentials file not found at {credentials_path}")
        print("Please ensure your service account JSON file is named 'client_secret.json'")
        print("and placed in the 'config' directory.")
        return

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = AnalyticsAdminServiceClient(credentials=credentials)

    print("Listing GA4 Properties:")

    # Iterate over all properties accessible by the service account
    for property_ in client.list_properties():
        print(f"  Property Name: {property_.display_name} ({property_.name})")


if __name__ == "__main__":
    list_properties()
