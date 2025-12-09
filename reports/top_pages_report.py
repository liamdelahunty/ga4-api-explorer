from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a report to get the top 25 pages by screen page views for a given date range.
    Returns the report data in a standardized format.
    """
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=25, # Default limit for top pages
        order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Top Pages report: {e}")
        return None

    # Standardized report data structure
    report_data = {
        "title": "Top 25 Pages by Views",
        "headers": ["Page Path", "Screen Page Views"],
        "rows": []
    }

    if not response.rows:
        return report_data # Return with empty rows

    for row in response.rows:
        page_path = row.dimension_values[0].value
        screen_page_views = row.metric_values[0].value
        report_data["rows"].append([page_path, screen_page_views])

    return report_data