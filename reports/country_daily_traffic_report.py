from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a report showing daily traffic for the Top 8 countries and an 'All Others' category.
    """
    
    # Define dimensions: Date and Country
    dimensions = [
        Dimension(name="date"),
        Dimension(name="country"),
    ]
    
    # Define metrics: Sessions, Active Users, Conversions, Engagement Rate
    metrics = [
        Metric(name="sessions"),
        Metric(name="activeUsers"),
        Metric(name="conversions"),
        Metric(name="engagementRate"),
    ]
    
    # Order by Date (ascending)
    order_bys = [
        OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"), desc=False),
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
        print(f"Error running Top 8 Countries Daily Traffic report: {e}")
        return {
            "title": "Top 8 Countries Daily Traffic",
            "headers": ["Date", "Country", "Sessions", "Users", "Conversions", "Eng. Rate"],
            "rows": [],
            "explanation": f"Error: {e}"
        }

    # First pass: Aggregate totals to identify Top 8 countries
    country_totals = {}
    temp_data = [] # Store raw row data temporarily
    all_dates = set()
    
    if response.rows:
        for row in response.rows:
            # Format date YYYYMMDD to YYYY-MM-DD
            raw_date = row.dimension_values[0].value
            date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            country = row.dimension_values[1].value
            sessions = int(row.metric_values[0].value)
            active_users = int(row.metric_values[1].value)
            conversions = float(row.metric_values[2].value)
            
            try:
                engagement_rate_val = float(row.metric_values[3].value)
            except (ValueError, TypeError):
                engagement_rate_val = 0.0
            
            country_totals[country] = country_totals.get(country, 0) + sessions
            all_dates.add(date)
            temp_data.append({
                "date": date,
                "country": country,
                "sessions": sessions,
                "users": active_users,
                "conversions": conversions,
                "engagement_val": engagement_rate_val
            })

    # Identify Top 8 countries
    sorted_countries = sorted(country_totals.items(), key=lambda item: item[1], reverse=True)
    top_8_names = [c for c, total in sorted_countries[:8] if total > 0]
    has_others = len(sorted_countries) > 8

    # Second pass: Re-aggregate into Top 8 + All Others
    data_matrix = {} # Structure: data[country][date] = metrics
    final_country_list = top_8_names + (["All Others"] if has_others else [])
    sorted_all_dates = sorted(list(all_dates))
    
    # Initialize matrix
    for name in final_country_list:
        data_matrix[name] = {}
        for d in sorted_all_dates:
            data_matrix[name][d] = {
                "sessions": 0, 
                "users": 0, 
                "conversions": 0, 
                "eng_sum": 0, 
                "count": 0,
                "engagement_rate": "0.00%"
            }

    for item in temp_data:
        date = item["date"]
        country = item["country"]
        target = country if country in top_8_names else "All Others"
        
        if target in data_matrix:
            m = data_matrix[target][date]
            m["sessions"] += item["sessions"]
            m["users"] += item["users"]
            m["conversions"] += item["conversions"]
            m["eng_sum"] += item["engagement_val"]
            m["count"] += 1

    # Finalise engagement rates
    for country in final_country_list:
        for date in sorted_all_dates:
            m = data_matrix[country][date]
            if m["count"] > 0:
                m["engagement_rate"] = f"{(m['eng_sum'] / m['count']) * 100:.2f}%"

    return {
        "title": "Top 8 Countries Daily Traffic Trend",
        "special_type": "top_campaign_daily_trend", # Reuse this template
        "category_label": "Country",
        "headers": ["Date", "Country", "Sessions", "Users", "Conversions", "Eng. Rate"],
        "rows": [], # Template uses json_data
        "json_data": data_matrix,
        "dates": sorted_all_dates,
        "campaign_names": final_country_list, # Template expects this key
        "explanation": (
            "This report shows daily traffic trends for the Top 8 countries by session volume.\n\n"
            "All other countries are aggregated into the **'All Others'** category.\n\n"
            "This view is particularly useful for spotting sudden spikes in traffic from specific regions, which can indicate bot or spam activity."
        )
    }
