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

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs a comparison report for Organic and Direct traffic growth.
    Compares the provided date range (After PPC) with a previous period.
    If the 'After' period is a full calendar month, the 'Before' period is the previous full month.
    Otherwise, it matches the day duration.
    """
    
    # 1. Calculate the "Before" period
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    
    # Check if 'After' period is exactly a full calendar month
    is_full_month = (start_date_obj.day == 1 and 
                     (end_date_obj + timedelta(days=1)).day == 1)
    
    if is_full_month:
        # Before period is the previous full calendar month
        before_end_date_obj = start_date_obj - timedelta(days=1)
        before_start_date_obj = before_end_date_obj.replace(day=1)
    else:
        # Standard duration matching
        duration = (end_date_obj - start_date_obj).days + 1
        before_end_date_obj = start_date_obj - timedelta(days=1)
        before_start_date_obj = before_end_date_obj - timedelta(days=duration - 1)
    
    before_start = before_start_date_obj.strftime("%Y-%m-%d")
    before_end = before_end_date_obj.strftime("%Y-%m-%d")
    
    def get_period_data(s_date, e_date, limit):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="landingPage")],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="newUsers"),
                Metric(name="engagementRate")
            ],
            date_ranges=[DateRange(start_date=s_date, end_date=e_date)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="sessionDefaultChannelGroup",
                    in_list_filter=Filter.InListFilter(
                        values=["Organic Search", "Direct"]
                    )
                )
            ),
            limit=limit,
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(metric_name="activeUsers"),
                    desc=True
                )
            ],
        )
        try:
            return data_client.run_report(request)
        except Exception as e:
            print(f"Error running period data: {e}")
            return None

    # 2. Fetch data for both periods
    # Current period (After PPC): Top 250 landing pages
    response_after = get_period_data(start_date, end_date, limit=250)
    # Previous period (Before PPC): Top 500 landing pages for intersection
    response_before = get_period_data(before_start, before_end, limit=500)

    if response_after is None or response_before is None:
        return None

    # 3. Process Results
    report_data = {
        "title": "Direct & Organic Acquisition Growth",
        "headers": [
            "Landing Page", 
            "Active Users (Before)", 
            "Active Users (After)", 
            "Growth (Active)", 
            "New Users (Before)",
            "New Users (After)",
            "Growth (New)",
            "Eng. Rate (After)"
        ],
        "rows": [],
        "explanation": f"### Comparison Period\n"
                       f"This report compares Organic Search and Direct traffic before and after PPC was stopped. \n\n"
                       f"**Before Period**: {before_start} to {before_end}\n"
                       f"**After Period**: {start_date} to {end_date}\n\n"
                       f"### Column Definitions\n"
                       f"* **Landing Page**: The URL path where the user first entered the site.\n"
                       f"* **Active Users (Before/After)**: Total number of active users in each period.\n"
                       f"* **Growth (Active)**: The raw difference in active users between the two periods, with the percentage change in brackets.\n"
                       f"* **New Users (Before/After)**: Total number of first-time users in each period.\n"
                       f"* **Growth (New)**: The raw difference in new users between the two periods, with the percentage change in brackets.\n"
                       f"* **Eng. Rate (After)**: The engagement rate (Engaged Sessions / Sessions) specifically for the 'After' period.\n\n"
                       f"### Methodology\n"
                       f"This report analyzes the top 250 landing pages from the current 'After' period. "
                       f"It then looks for these specific pages within the top 500 landing pages of the previous 'Before' period. "
                       f"A value of **0** or **(New)** in the 'Before' column indicates the page was not among the top 500 pages in that period."
    }

    # Map: { landing_page: { 'before': metrics, 'after': metrics } }
    pages_data = {}

    # First, populate with the 250 pages from the AFTER period
    if response_after.rows:
        for row in response_after.rows:
            lp = row.dimension_values[0].value
            pages_data[lp] = {
                "before": {"activeUsers": 0, "newUsers": 0},
                "after": {
                    "activeUsers": int(row.metric_values[0].value),
                    "newUsers": int(row.metric_values[1].value),
                    "rate": float(row.metric_values[2].value)
                }
            }

    # Then, intersect with the 500 pages from the BEFORE period
    if response_before.rows:
        for row in response_before.rows:
            lp = row.dimension_values[0].value
            if lp in pages_data:
                pages_data[lp]["before"]["activeUsers"] = int(row.metric_values[0].value)
                pages_data[lp]["before"]["newUsers"] = int(row.metric_values[1].value)

    if not pages_data:
        return report_data

    for landing_page, data in pages_data.items():
        active_before = data["before"]["activeUsers"]
        active_after = data["after"]["activeUsers"]
        new_before = data["before"]["newUsers"]
        new_after = data["after"]["newUsers"]
        rate_after = data["after"]["rate"]
        
        # Active User Growth
        growth_active = active_after - active_before
        pct_active = f" ({((growth_active / active_before) * 100):+.1f}%)" if active_before > 0 else " (New)"
        
        # New User Growth
        growth_new = new_after - new_before
        pct_new = f" ({((growth_new / new_before) * 100):+.1f}%)" if new_before > 0 else " (New)"
        
        report_data["rows"].append([
            landing_page,
            str(active_before),
            str(active_after),
            f"{growth_active:+d}{pct_active}",
            str(new_before),
            str(new_after),
            f"{growth_new:+d}{pct_new}",
            f"{rate_after * 100:.2f}%"
        ])

    # Sort by Active Users (After) - column index 2
    report_data["rows"].sort(key=lambda x: int(x[2]), reverse=True)

    return report_data
