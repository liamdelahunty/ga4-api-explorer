from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy
import json

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a Top Hostnames Comparison report.
    Fetches multi-month data for all hostnames to allow dynamic ranking and multi-line comparison in HTML.
    """
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="hostName"),
            Dimension(name="yearMonth")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="engagedSessions"),
            Metric(name="engagementRate")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="yearMonth"))]
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Top Hostnames Comparison Report: {e}")
        return None

    # Nested structure for JS: data[hostname][month] = { metrics }
    data_matrix = {}
    all_months = set()
    all_hostnames = set()

    for row in response.rows:
        hostname = row.dimension_values[0].value
        ym = row.dimension_values[1].value
        month_str = f"{ym[:4]}-{ym[4:]}"
        
        all_months.add(month_str)
        all_hostnames.add(hostname)
        
        if hostname not in data_matrix: 
            data_matrix[hostname] = {}
        
        data_matrix[hostname][month_str] = {
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
            "engaged": int(row.metric_values[2].value),
            "rate": f"{float(row.metric_values[3].value) * 100:.2f}%"
        }

    return {
        "title": "Top Hostnames Comparison",
        "special_type": "top_hostnames_comparison",
        "json_data": data_matrix,
        "months": sorted(list(all_months)),
        "hostnames": sorted(list(all_hostnames)),
        "headers": ["Hostname", "Month", "Sessions"], # Fallback
        "rows": [], # Fallback
        "explanation": "This report allows you to compare traffic trends across multiple hostnames (subdomains) on a single chart. You can toggle specific hostnames to isolate trends and identify when new domains started contributing significantly to your overall traffic."
    }
