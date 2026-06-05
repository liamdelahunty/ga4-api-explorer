from google.analytics.data_v1beta.types import (
    RunReportRequest, 
    DateRange, 
    Dimension, 
    Metric, 
    OrderBy, 
    FilterExpression, 
    Filter
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_earliest_data_date(property_id, data_client):
    """
    Finds the earliest date with data for a given property by querying the API.
    """
    start_date = "2020-01-01"
    end_date = datetime.now().strftime('%Y-%m-%d')

    try:
        response = data_client.run_report(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"), desc=False)],
            limit=1
        )
        if response.rows:
            earliest_date_str = response.rows[0].dimension_values[0].value
            return datetime.strptime(earliest_date_str, '%Y%m%d').date()
    except Exception as e:
        print(f"Error discovering the earliest data date: {e}")
        return None
    return None

def run_report(property_id, data_client, start_date=None, end_date=None):
    """
    Runs a report that takes a calendar month view of direct, organic, and cpc traffic.
    Includes active and new users. Splits data into Source / Medium and Just Medium.
    """
    
    # 1. Determine Date Range
    if not start_date:
        earliest_date = get_earliest_data_date(property_id, data_client)
        if not earliest_date:
            # Fallback if discovery fails
            start_date = (datetime.now() - relativedelta(years=2)).strftime("%Y-%m-01")
        else:
            start_date = earliest_date.replace(day=1).strftime("%Y-%m-%d")
    
    if not end_date:
        # Latest complete month
        last_day_prev_month = datetime.now().replace(day=1) - timedelta(days=1)
        end_date = last_day_prev_month.strftime("%Y-%m-%d")

    # 2. Run GA4 Report
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="yearMonth"),
            Dimension(name="sessionSourceMedium"),
            Dimension(name="sessionMedium")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="sessionMedium",
                in_list_filter=Filter.InListFilter(
                    values=["(none)", "organic", "cpc"]
                )
            )
        ),
        order_bys=[
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="yearMonth"), desc=False)
        ]
    )

    try:
        response = data_client.run_report(request)
    except Exception as e:
        print(f"Error running Monthly Traffic Source Report: {e}")
        return None

    # 3. Process Data
    # We need to structure data for both reports: Source/Medium and Medium
    sm_data = {} # { "Source / Medium": { "YYYY-MM": { "active": X, "new": Y } } }
    m_data = {}  # { "Medium": { "YYYY-MM": { "active": X, "new": Y } } }
    months_set = set()

    if response.rows:
        for row in response.rows:
            year_month = row.dimension_values[0].value
            formatted_month = f"{year_month[:4]}-{year_month[4:]}"
            source_medium = row.dimension_values[1].value
            medium = row.dimension_values[2].value
            
            active = int(row.metric_values[0].value)
            new = int(row.metric_values[1].value)
            
            months_set.add(formatted_month)
            
            # Source / Medium Aggregation - Exactly 7 categories as requested
            sm_lower = source_medium.lower()
            m_lower = medium.lower()
            
            if 'organic' in m_lower:
                if 'google' in sm_lower: group = "Google Organic"
                elif 'bing' in sm_lower: group = "Bing Organic"
                else: group = "Other Organic"
            elif 'cpc' in m_lower:
                if 'google' in sm_lower: group = "Google CPC"
                elif 'bing' in sm_lower: group = "Bing CPC"
                else: group = "Other CPC"
            else:
                group = "Direct"

            if group not in sm_data:
                sm_data[group] = {}
            if formatted_month not in sm_data[group]:
                sm_data[group][formatted_month] = {"active": 0, "new": 0}
            sm_data[group][formatted_month]["active"] += active
            sm_data[group][formatted_month]["new"] += new
            
            # Medium Aggregation
            if medium not in m_data:
                m_data[medium] = {}
            if formatted_month not in m_data[medium]:
                m_data[medium][formatted_month] = {"active": 0, "new": 0}
            m_data[medium][formatted_month]["active"] += active
            m_data[medium][formatted_month]["new"] += new

    sorted_months = sorted(list(months_set))

    # Standard rows for console/CSV (Side-by-side comparison)
    headers = [
        "Month", 
        "Direct Active", "Direct New",
        "Organic Active", "Organic New",
        "CPC Active", "CPC New"
    ]
    rows = []
    for m in sorted_months:
        d = m_data.get('(none)', {}).get(m, {"active": 0, "new": 0})
        o = m_data.get('organic', {}).get(m, {"active": 0, "new": 0})
        c = m_data.get('cpc', {}).get(m, {"active": 0, "new": 0})
        
        rows.append([
            m,
            str(d["active"]), str(d["new"]),
            str(o["active"]), str(o["new"]),
            str(c["active"]), str(c["new"])
        ])

    # Define a preferred order for Source / Medium groups (Exactly 7 rows)
    preferred_order = [
        "Google Organic", "Google CPC",
        "Bing Organic", "Bing CPC",
        "Other Organic", "Other CPC",
        "Direct"
    ]
    # Filter to only those present
    sm_keys = [k for k in preferred_order if k in sm_data]

    report_data = {
        "title": "Monthly Traffic Source Trend (Direct, Organic, CPC)",
        "special_type": "monthly_traffic_source_report",
        "headers": headers,
        "rows": rows,
        "date_range": f"{start_date} to {end_date}",
        "months": sorted_months,
        "sm_data": sm_data,
        "m_data": m_data,
        "sm_keys": sm_keys,
        "m_keys": sorted(m_data.keys()),
        "explanation": f"This report provides a monthly overview of traffic from Direct, Organic, and CPC sources.\n\n"
                       f"**Earliest data found**: {start_date}\n"
                       f"**Latest complete month**: {end_date}\n\n"
                       f"The data is split into two views in the HTML report:\n"
                       f"1. **Source / Medium**: Granular view of specific source/medium combinations.\n"
                       f"2. **Medium**: High-level view by traffic medium."
    }

    return report_data
