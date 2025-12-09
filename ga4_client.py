from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
import os

def get_admin_client():
    """Returns an authenticated Google Analytics Admin API client."""
    credentials = _load_credentials()
    if credentials:
        return AnalyticsAdminServiceClient(credentials=credentials)
    return None

def get_data_client():
    """Returns an authenticated Google Analytics Data API client."""
    credentials = _load_credentials()
    if credentials:
        return BetaAnalyticsDataClient(credentials=credentials)
    return None

def _load_credentials():
    """Loads credentials from the client_secret.json file."""
    # Construct the path to the credentials file
    script_dir = os.path.dirname(__file__)
    credentials_path = os.path.join(script_dir, "config", "client_secret.json")

    # Check if the credentials file exists
    if not os.path.exists(credentials_path):
        print(f"Error: Credentials file not found at {credentials_path}")
        print("Please ensure your service account JSON file is named 'client_secret.json'")
        print("and placed in the 'config' directory.")
        return None

    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return credentials
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

