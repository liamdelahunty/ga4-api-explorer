from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy
import json

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a report to track traffic trends by Hostname using yearMonth.
    This helps identify when traffic from various subdomains started appearing.
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
        order_bys=[
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="yearMonth")),
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="hostName"))
        ]
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Hostname Traffic Trend Report: {e}")
        return None

    # Structure: data[hostname][month] = { metrics }
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
        
        try:
            rate = f"{float(row.metric_values[3].value) * 100:.2f}%"
        except:
            rate = row.metric_values[3].value

        data_matrix[hostname][month_str] = {
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
            "engaged": int(row.metric_values[2].value),
            "rate": rate
        }

    sorted_months = sorted(list(all_months))
    sorted_hostnames = sorted(list(all_hostnames))

    report_data = {
        "title": "Hostname Traffic Trend",
        "special_type": "hostname-traffic-trend",
        "json_data": data_matrix,
        "months": sorted_months,
        "hostnames": sorted_hostnames,
        "headers": ["Hostname", "Month", "Sessions", "Active Users", "Engaged Sessions", "Engagement Rate"],
        "rows": [],
        "explanation": "This report shows traffic trends by hostname to identify when specific subdomains started appearing in the analytics data. This is useful for investigating cross-domain tracking issues or unexpected traffic influxes."
    }

    # Fill rows for CSV fallback
    for hostname in sorted_hostnames:
        for month in sorted_months:
            m_data = data_matrix[hostname].get(month, {"sessions": 0, "users": 0, "engaged": 0, "rate": "0.00%"})
            report_data["rows"].append([
                hostname, 
                month, 
                m_data["sessions"], 
                m_data["users"], 
                m_data["engaged"], 
                m_data["rate"]
            ])

    return report_data
