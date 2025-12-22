# reports/traffic_acquisition_report.py

from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric, OrderBy, DateRange

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a detailed Traffic Acquisition report, including engagement and conversion metrics,
    ordered by the total number of users.
    """
    
    # Define the dimensions and metrics for the report.
    # This report provides a comprehensive view of how different channels are performing.
    dimensions = [
        Dimension(name="sessionDefaultChannelGroup"),
        Dimension(name="sessionSourceMedium"),
    ]
    metrics = [
        Metric(name="totalUsers"),
        Metric(name="newUsers"),
        Metric(name="engagedSessions"),
        Metric(name="engagementRate"),
        Metric(name="conversions"), # Note: This will sum ALL conversion events.
    ]
    
    # Order the results by the total number of users in descending order
    # to see the most significant traffic sources first.
    order_bys = [
        OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name="totalUsers"),
            desc=True
        ),
    ]

    # Create the report request
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=dimensions,
        metrics=metrics,
        order_bys=order_bys,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    # Execute the report request
    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Traffic Acquisition report: {e}")
        return None

    # Process the response and format it into the standardized dictionary.
    
    # Extract headers for dimensions and metrics
    report_headers = [header.name for header in response.dimension_headers] + [header.name for header in response.metric_headers]
    
    # Process each row of the response
    report_rows = []
    for row in response.rows:
        row_data = []
        # Add dimension values
        for value in row.dimension_values:
            row_data.append(value.value)
        # Add metric values, formatting floats where necessary
        for i, value in enumerate(row.metric_values):
            # The 'engagementRate' metric is a float (e.g., 0.65), so we format it as a percentage.
            if response.metric_headers[i].name == 'engagementRate':
                try:
                    # Format as a percentage with two decimal places.
                    rate = float(value.value) * 100
                    row_data.append(f"{rate:.2f}%")
                except (ValueError, TypeError):
                    row_data.append(value.value)
            else:
                row_data.append(value.value)
        report_rows.append(row_data)

    report_data = {
        "title": "Traffic Acquisition Report",
        "headers": report_headers,
        "rows": report_rows,
    }

    return report_data
