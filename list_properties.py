from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient


def list_properties():
    """Lists GA4 properties accessible by the authenticated service account."""
    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = AnalyticsAdminServiceClient()

    print("Listing GA4 Properties:")

    # Iterate over all properties accessible by the service account
    for property_ in client.list_properties():
        print(f"  Property Name: {property_.display_name} ({property_.name})")


if __name__ == "__main__":
    list_properties()
