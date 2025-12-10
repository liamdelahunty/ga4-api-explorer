# reports/user_acquisition_report.py

from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric, OrderBy

def run_report(property_id, data_client, start_date, end_date):
    """Runs a report on user acquisition by session source/medium."""
    
    # Define the dimensions and metrics for the report
    dimensions = [
        Dimension(name="sessionSourceMedium"),
    ]
    metrics = [
        Metric(name="newUsers"),
    ]
    order_bys = [
        OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name="newUsers"),
            desc=True
        ),
    ]

    # Create the report request
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=dimensions,
        metrics=metrics,
        order_bys=order_bys,
        date_ranges=[{"start_date": start_date, "end_date": end_date}],
    )

    # Execute the report request
    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running user acquisition report: {e}")
        return None

    # Process the response and format it into a dictionary
    headers = [header.name for header in response.dimension_headers] + [header.name for header in response.metric_headers]
    rows = []
    for row in response.rows:
        rows.append([value.value for value in row.dimension_values] + [value.value for value in row.metric_values])

    report_data = {
        "title": "User Acquisition Report",
        "headers": headers,
        "rows": rows,
    }

    return report_data
