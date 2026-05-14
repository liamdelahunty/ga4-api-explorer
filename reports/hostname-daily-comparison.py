from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy
import json

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a Hostname Daily Comparison report.
    Fetches daily data for hostnames to identify specific dates of traffic changes.
    """
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="hostName"),
            Dimension(name="date")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="engagedSessions")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))]
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Hostname Daily Comparison Report: {e}")
        return None

    # Nested structure for JS: data[hostname][date] = { metrics }
    data_matrix = {}
    all_dates = set()
    all_hostnames = set()

    for row in response.rows:
        hostname = row.dimension_values[0].value
        d_raw = row.dimension_values[1].value
        date_str = f"{d_raw[:4]}-{d_raw[4:6]}-{d_raw[6:]}"
        
        all_dates.add(date_str)
        all_hostnames.add(hostname)
        
        if hostname not in data_matrix: 
            data_matrix[hostname] = {}
        
        data_matrix[hostname][date_str] = {
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
            "engaged": int(row.metric_values[2].value)
        }

    sorted_dates = sorted(list(all_dates))
    sorted_hostnames = sorted(list(all_hostnames))

    # Prepare rows for CSV
    rows = []
    for hostname in sorted_hostnames:
        for d in sorted_dates:
            d_data = data_matrix[hostname].get(d, {"sessions": 0, "users": 0, "engaged": 0})
            rows.append([
                hostname, 
                d, 
                d_data["sessions"], 
                d_data["users"], 
                d_data["engaged"]
            ])

    return {
        "title": "Hostname Daily Comparison",
        "special_type": "hostname-daily-comparison",
        "json_data": data_matrix,
        "dates": sorted_dates,
        "hostnames": sorted_hostnames,
        "headers": ["Hostname", "Date", "Sessions", "Active Users", "Engaged Sessions"],
        "rows": rows,
        "explanation": "This report provides a daily breakdown of traffic by hostname. Use this to pinpoint the exact date when unexpected hostnames (contamination) began appearing in your data."
    }
