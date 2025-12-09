from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest


def main():
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Replace with your GA4 property ID before running.
    property_id = "YOUR-GA4-PROPERTY-ID"

    # Explicitly load credentials from the service account key file.
    # Make sure your service account JSON file is in the 'config' directory
    # and named 'client_secret.json'.
    from google.oauth2 import service_account
    import os

    # Construct the path to the credentials file
    credentials_path = os.path.join(os.path.dirname(__file__), "config", "client_secret.json")

    # Check if the credentials file exists
    if not os.path.exists(credentials_path):
        print(f"Error: Credentials file not found at {credentials_path}")
        print("Please ensure your service account JSON file is named 'client_secret.json'")
        print("and placed in the 'config' directory.")
        return

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = BetaAnalyticsDataClient(credentials=credentials)

    # To learn more about constructing a request, see:
    # https://developers.google.com/analytics/devguides/reporting/data/v1/basics
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[{"name": "city"}],
        metrics=[{"name": "activeUsers"}],
    )
    response = client.run_report(request)

    print("Report result:")
    for row in response.rows:
        print(row.dimension_values[0].value, row.metric_values[0].value)


if __name__ == "__main__":
    main()
