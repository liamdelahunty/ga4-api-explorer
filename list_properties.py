from google.analytics.admin_v1alpha.types import ListPropertiesRequest
import ga4_client # Import our new client module

def list_accounts_and_properties():
    """Lists GA4 accounts and then properties accessible by the authenticated service account."""
    client = ga4_client.get_admin_client()
    if not client:
        return

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
