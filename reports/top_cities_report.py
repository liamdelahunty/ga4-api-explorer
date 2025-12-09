from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a report to get the top 5 cities by active users for a given date range.
    Returns the report data in a standardized format.
    """
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=5,
        order_bys=[{"metric": {"metric_name": "activeUsers"}, "desc": True}],
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running top cities report: {e}")
        return None

    # Standardized report data structure
    report_data = {
        "title": "Top 5 Cities by Active Users",
        "headers": ["City", "Active Users"],
        "rows": []
    }

    if not response.rows:
        return report_data # Return with empty rows

    for row in response.rows:
        city = row.dimension_values[0].value
        active_users = row.metric_values[0].value
        report_data["rows"].append([city, active_users])

    return report_data
