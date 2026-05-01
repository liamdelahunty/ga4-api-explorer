from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a report showing traffic by country and hour of the day.
    """
    
    # Define dimensions: Hour and Country
    dimensions = [
        Dimension(name="hour"),
        Dimension(name="country"),
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
        print(f"Error running Country Traffic by Hour report: {e}")
        return {
            "title": "Traffic by Country and Hour",
            "headers": ["Hour", "Country", "Sessions", "Active Users", "Engagement Rate"],
            "rows": [],
            "explanation": f"Error: {e}"
        }

    report_headers = ["Hour", "Country", "Sessions", "Active Users", "Engagement Rate"]
    
    # First pass: Aggregate totals to identify which countries have actual session traffic
    country_totals = {}
    temp_data = [] # Store raw row data temporarily
    
    if response.rows:
        for row in response.rows:
            hour = row.dimension_values[0].value
            country = row.dimension_values[1].value
            sessions = int(row.metric_values[0].value)
            active_users = int(row.metric_values[1].value)
            
            if sessions == 0 and active_users == 0:
                continue
                
            try:
                engagement_rate_val = float(row.metric_values[2].value)
                engagement_rate_str = f"{engagement_rate_val * 100:.2f}%"
            except (ValueError, TypeError):
                engagement_rate_str = row.metric_values[2].value
            
            country_totals[country] = country_totals.get(country, 0) + sessions
            temp_data.append({
                "hour": hour,
                "country": country,
                "sessions": sessions,
                "users": active_users,
                "engagement": engagement_rate_str
            })

    # Filter: Only keep TOP 10 countries by total sessions
    sorted_countries = sorted(country_totals.items(), key=lambda item: item[1], reverse=True)
    filtered_countries = [c for c, total in sorted_countries[:10] if total > 0]
    
    # Second pass: Build the final report data using only the filtered countries
    report_rows = []
    data_matrix = {}
    all_hours = [f"{i:02d}" for i in range(24)]

    for item in temp_data:
        country = item["country"]
        if country in filtered_countries:
            hour = item["hour"]
            report_rows.append([
                hour,
                country,
                str(item["sessions"]),
                str(item["users"]),
                item["engagement"]
            ])
            
            if hour not in data_matrix:
                data_matrix[hour] = {}
            data_matrix[hour][country] = {
                "sessions": item["sessions"],
                "users": item["users"],
                "engagement": item["engagement"]
            }

    return {
        "title": "Traffic by Country and Hour",
        "special_type": "channel_traffic_by_hour", # Re-use template logic
        "category_label": "Country",
        "headers": report_headers,
        "rows": report_rows,
        "json_data": data_matrix,
        "hours": all_hours,
        "channels": sorted(filtered_countries), # Template uses 'channels' key for chip labels
        "explanation": (
            "This report shows how traffic from different countries is distributed across the hours of the day.\n\n"
            "**Hour:** The hour of the day in the property's timezone.\n"
            "**Country:** The country of the user.\n"
            "**Sessions:** The number of sessions that began in that hour.\n"
            "**Active Users:** The number of distinct users who had an engaged session in that hour."
        )
    }
