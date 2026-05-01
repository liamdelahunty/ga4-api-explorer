from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a report showing channel traffic by hour of the day.
    """
    
    # Define dimensions: Hour and Channel
    dimensions = [
        Dimension(name="hour"),
        Dimension(name="sessionDefaultChannelGroup"),
    ]
    
    # Define metrics: Sessions, Active Users, Engagement Rate
    metrics = [
        Metric(name="sessions"),
        Metric(name="activeUsers"),
        Metric(name="engagementRate"),
    ]
    
    # Order by Hour (ascending) and then Sessions (descending)
    order_bys = [
        OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="hour"), desc=False),
        OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True),
    ]

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=dimensions,
        metrics=metrics,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=order_bys,
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Channel Traffic by Hour report: {e}")
        return {
            "title": "Channel Traffic by Hour of Day",
            "headers": ["Hour", "Channel", "Sessions", "Active Users", "Engagement Rate"],
            "rows": [],
            "explanation": f"Error: {e}"
        }

    report_headers = ["Hour", "Channel", "Sessions", "Active Users", "Engagement Rate"]
    report_rows = []

    if response.rows:
        for row in response.rows:
            hour = row.dimension_values[0].value
            channel = row.dimension_values[1].value
            sessions = row.metric_values[0].value
            active_users = row.metric_values[1].value
            
            try:
                engagement_rate = f"{float(row.metric_values[2].value) * 100:.2f}%"
            except (ValueError, TypeError):
                engagement_rate = row.metric_values[2].value
                
            report_rows.append([
                hour,
                channel,
                sessions,
                active_users,
                engagement_rate
            ])

    return {
        "title": "Channel Traffic by Hour of Day",
        "headers": report_headers,
        "rows": report_rows,
        "explanation": (
            "This report shows how traffic from different channels is distributed across the hours of the day (00-23).\n\n"
            "**Hour:** The hour of the day in the property's timezone.\n"
            "**Channel:** The Session Default Channel Group.\n"
            "**Sessions:** The number of sessions that began in that hour.\n"
            "**Active Users:** The number of distinct users who had an engaged session in that hour.\n"
            "**Engagement Rate:** The percentage of sessions that were engaged sessions."
        )
    }
