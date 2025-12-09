from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient
from google.analytics.admin_v1alpha.types import ListPropertiesRequest
from google.oauth2 import service_account
import os

def list_accounts_and_properties():
    """Lists GA4 accounts and then properties accessible by the authenticated service account."""
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

    print("Listing GA4 Accounts and Properties:")

    # First, list all accessible accounts
    accounts = []
    for account in client.list_accounts():
        accounts.append(account)
        print(f"Account Name: {account.display_name} ({account.name})")

    if not accounts:
        print("No GA4 accounts found that are accessible by this service account.")
        return

    # Now, for each account, list its properties
    for account in accounts:
        print(f"\nProperties for Account: {account.display_name} ({account.name})")
        # Create a ListPropertiesRequest filtered by the current account
        request = ListPropertiesRequest(
            filter=f"ancestor:{account.name}"
        )

        properties_found = False
        for property_ in client.list_properties(request=request):
            properties_found = True
            print(f"  Property Name: {property_.display_name} ({property_.name})")
        
        if not properties_found:
            print(f"  No properties found for account {account.display_name}.")


if __name__ == "__main__":
    list_accounts_and_properties()
