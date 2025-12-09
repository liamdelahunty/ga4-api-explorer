from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest


def main():
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Replace with your GA4 property ID before running.
    property_id = "YOUR-GA4-PROPERTY-ID"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()

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
