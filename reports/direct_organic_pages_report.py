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
    Compares the provided date range (After PPC) with a previous period of the same length (Before PPC).
    """
    
    # 1. Calculate the "Before" period
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    duration = (end_date_obj - start_date_obj).days + 1
    
    before_end_date_obj = start_date_obj - timedelta(days=1)
    before_start_date_obj = before_end_date_obj - timedelta(days=duration - 1)
    
    before_start = before_start_date_obj.strftime("%Y-%m-%d")
    before_end = before_end_date_obj.strftime("%Y-%m-%d")
    
    def get_period_data(s_date, e_date):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="landingPage")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
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
            limit=500,
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(metric_name="sessions"),
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
    response_after = get_period_data(start_date, end_date)
    response_before = get_period_data(before_start, before_end)

    if response_after is None or response_before is None:
        return None

    # 3. Process Results
    report_data = {
        "title": "Direct & Organic Acquisition Growth",
        "headers": [
            "Landing Page", 
            f"Sessions ({before_start})", 
            f"Sessions ({start_date})", 
            "Growth (Sessions)", 
            f"Users ({before_start})",
            f"Users ({start_date})",
            "Growth (Users)",
            "Eng. Rate (After)"
        ],
        "rows": [],
        "explanation": f"### Comparison Period\n"
                       f"This report compares Organic Search and Direct traffic before and after PPC was stopped. \n\n"
                       f"**Before Period**: {before_start} to {before_end}\n"
                       f"**After Period**: {start_date} to {end_date}\n\n"
                       f"### Column Definitions\n"
                       f"* **Landing Page**: The URL path where the user first entered the site.\n"
                       f"* **Sessions (Before/After)**: Total number of sessions initiated via Organic or Direct channels in each period.\n"
                       f"* **Growth (Sessions)**: The raw difference in sessions between the two periods, with the percentage change in brackets.\n"
                       f"* **Users (Before/After)**: Total number of active users in each period.\n"
                       f"* **Growth (Users)**: The raw difference in active users between the two periods, with the percentage change in brackets.\n"
                       f"* **Eng. Rate (After)**: The engagement rate (Engaged Sessions / Sessions) specifically for the 'After' period.\n\n"
                       f"Landing pages are ranked by total sessions in the 'After' period. "
                       f"Note: This report captures up to 500 landing pages per period; pages outside the top 500 in a specific period may appear as 0 or 'New'."
    }

    # Map: { landing_page: { 'before': metrics, 'after': metrics } }
    pages_data = {}

    def process_response(response, period):
        if not response or not response.rows:
            return
        for row in response.rows:
            lp = row.dimension_values[0].value
            if lp not in pages_data:
                pages_data[lp] = {
                    "before": {"sessions": 0, "users": 0, "rate": 0.0},
                    "after": {"sessions": 0, "users": 0, "rate": 0.0}
                }
            pages_data[lp][period]["sessions"] = int(row.metric_values[0].value)
            pages_data[lp][period]["users"] = int(row.metric_values[1].value)
            if period == "after":
                pages_data[lp][period]["rate"] = float(row.metric_values[2].value)

    process_response(response_after, "after")
    process_response(response_before, "before")

    if not pages_data:
        return report_data

    for landing_page, data in pages_data.items():
        sess_before = data["before"]["sessions"]
        sess_after = data["after"]["sessions"]
        users_before = data["before"]["users"]
        users_after = data["after"]["users"]
        rate_after = data["after"]["rate"]
        
        # Session Growth
        growth_sess = sess_after - sess_before
        pct_sess = f" ({((growth_sess / sess_before) * 100):+.1f}%)" if sess_before > 0 else " (New)"
        
        # User Growth
        growth_users = users_after - users_before
        pct_users = f" ({((growth_users / users_before) * 100):+.1f}%)" if users_before > 0 else " (New)"
        
        report_data["rows"].append([
            landing_page,
            str(sess_before),
            str(sess_after),
            f"{growth_sess:+d}{pct_sess}",
            str(users_before),
            str(users_after),
            f"{growth_users:+d}{pct_users}",
            f"{rate_after * 100:.2f}%"
        ])

    # Re-sort by sessions (After)
    report_data["rows"].sort(key=lambda x: int(x[2]), reverse=True)

    return report_data


    for landing_page, data in pages_data.items():
        sess_before = data["before"]["sessions"]
        sess_after = data["after"]["sessions"]
        users_before = data["before"]["users"]
        users_after = data["after"]["users"]
        rate_after = data["after"]["rate"]
        
        # Session Growth
        growth_sess = sess_after - sess_before
        pct_sess = f" ({((growth_sess / sess_before) * 100):+.1f}%)" if sess_before > 0 else " (New)"
        
        # User Growth
        growth_users = users_after - users_before
        pct_users = f" ({((growth_users / users_before) * 100):+.1f}%)" if users_before > 0 else " (New)"
        
        report_data["rows"].append([
            landing_page,
            str(sess_before),
            str(sess_after),
            f"{growth_sess:+d}{pct_sess}",
            str(users_before),
            str(users_after),
            f"{growth_users:+d}{pct_users}",
            f"{rate_after * 100:.2f}%"
        ])

    # Re-sort by sessions (After)
    report_data["rows"].sort(key=lambda x: int(x[2]), reverse=True)

    return report_data
