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
    """
    
    # 1. Calculate the "Before" period
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    
    is_full_month = (start_date_obj.day == 1 and 
                     (end_date_obj + timedelta(days=1)).day == 1)
    
    if is_full_month:
        before_end_date_obj = start_date_obj - timedelta(days=1)
        before_start_date_obj = before_end_date_obj.replace(day=1)
    else:
        duration = (end_date_obj - start_date_obj).days + 1
        before_end_date_obj = start_date_obj - timedelta(days=1)
        before_start_date_obj = before_end_date_obj - timedelta(days=duration - 1)
    
    before_start = before_start_date_obj.strftime("%Y-%m-%d")
    before_end = before_end_date_obj.strftime("%Y-%m-%d")
    
    def get_period_data(s_date, e_date, limit):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="landingPage"),
                Dimension(name="sessionDefaultChannelGroup")
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="newUsers"),
                Metric(name="sessions"),
                Metric(name="engagedSessions")
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
    # Increased limits to account for dimension split
    response_after = get_period_data(start_date, end_date, limit=500)
    response_before = get_period_data(before_start, before_end, limit=1000)

    if response_after is None or response_before is None:
        return None

    # 3. Process Results
    pages_data = {}
    lp_channel_data = {}

    if response_after.rows:
        for row in response_after.rows:
            lp = row.dimension_values[0].value
            channel = row.dimension_values[1].value
            active = int(row.metric_values[0].value)
            new = int(row.metric_values[1].value)
            sessions = int(row.metric_values[2].value)
            engaged = int(row.metric_values[3].value)
            
            if lp not in pages_data:
                pages_data[lp] = {
                    "before": {"activeUsers": 0, "newUsers": 0},
                    "after": {"activeUsers": 0, "newUsers": 0, "sessions": 0, "engaged": 0}
                }
                lp_channel_data[lp] = {}
            
            if channel not in lp_channel_data[lp]:
                lp_channel_data[lp][channel] = {
                    "before": {"active": 0, "new": 0},
                    "after": {"active": 0, "new": 0}
                }
            
            pages_data[lp]["after"]["activeUsers"] += active
            pages_data[lp]["after"]["newUsers"] += new
            pages_data[lp]["after"]["sessions"] += sessions
            pages_data[lp]["after"]["engaged"] += engaged
            
            lp_channel_data[lp][channel]["after"]["active"] += active
            lp_channel_data[lp][channel]["after"]["new"] += new

    # Get top 250 landing pages by active users
    top_lps = sorted(pages_data.keys(), key=lambda x: pages_data[x]["after"]["activeUsers"], reverse=True)[:250]
    pages_data = {lp: pages_data[lp] for lp in top_lps}
    lp_channel_data = {lp: lp_channel_data[lp] for lp in top_lps}

    if response_before.rows:
        for row in response_before.rows:
            lp = row.dimension_values[0].value
            channel = row.dimension_values[1].value
            active = int(row.metric_values[0].value)
            new = int(row.metric_values[1].value)
            
            if lp in pages_data:
                pages_data[lp]["before"]["activeUsers"] += active
                pages_data[lp]["before"]["newUsers"] += new
                
                if channel not in lp_channel_data[lp]:
                    lp_channel_data[lp][channel] = {"before": {"active": 0, "new": 0}, "after": {"active": 0, "new": 0}}
                lp_channel_data[lp][channel]["before"]["active"] += active
                lp_channel_data[lp][channel]["before"]["new"] += new

    # 4. Calculate Summary Metrics (Top 250 Pages)
    channel_summary = {
        "Organic Search": {"before": {"active": 0, "new": 0}, "after": {"active": 0, "new": 0}},
        "Direct": {"before": {"active": 0, "new": 0}, "after": {"active": 0, "new": 0}}
    }
    for lp in top_lps:
        for channel, data in lp_channel_data[lp].items():
            if channel in channel_summary:
                channel_summary[channel]["before"]["active"] += data["before"]["active"]
                channel_summary[channel]["before"]["new"] += data["before"]["new"]
                channel_summary[channel]["after"]["active"] += data["after"]["active"]
                channel_summary[channel]["after"]["new"] += data["after"]["new"]

    total_active_before = sum(c["before"]["active"] for c in channel_summary.values())
    total_active_after = sum(c["after"]["active"] for c in channel_summary.values())
    total_new_before = sum(c["before"]["new"] for c in channel_summary.values())
    total_new_after = sum(c["after"]["new"] for c in channel_summary.values())

    # Generate Summary Table HTML
    summary_table_html = """
    <table class="table table-sm table-bordered mb-0">
        <thead class="table-light">
            <tr>
                <th>Channel</th>
                <th>Active (Before)</th>
                <th>Active (After)</th>
                <th>Growth (Active)</th>
                <th>New (Before)</th>
                <th>New (After)</th>
                <th>Growth (New)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for channel in ["Organic Search", "Direct"]:
        b_a = channel_summary[channel]["before"]["active"]
        a_a = channel_summary[channel]["after"]["active"]
        b_n = channel_summary[channel]["before"]["new"]
        a_n = channel_summary[channel]["after"]["new"]
        
        g_a = a_a - b_a
        p_a = f" ({((g_a / b_a) * 100):+.1f}%)" if b_a > 0 else " (New)"
        
        g_n = a_n - b_n
        p_n = f" ({((g_n / b_n) * 100):+.1f}%)" if b_n > 0 else " (New)"
        
        summary_table_html += f"""
            <tr>
                <td>{channel}</td>
                <td>{b_a:,}</td>
                <td>{a_a:,}</td>
                <td>{g_a:+,}{p_a}</td>
                <td>{b_n:,}</td>
                <td>{a_n:,}</td>
                <td>{g_n:+,}{p_n}</td>
            </tr>
        """
    
    t_g_a = total_active_after - total_active_before
    t_p_a = f" ({((t_g_a / total_active_before) * 100):+.1f}%)" if total_active_before > 0 else ""
    t_g_n = total_new_after - total_new_before
    t_p_n = f" ({((t_g_n / total_new_before) * 100):+.1f}%)" if total_new_before > 0 else ""
    
    summary_table_html += f"""
            <tr class="table-light fw-bold">
                <td>Total</td>
                <td>{total_active_before:,}</td>
                <td>{total_active_after:,}</td>
                <td>{t_g_a:+,}{t_p_a}</td>
                <td>{total_new_before:,}</td>
                <td>{total_new_after:,}</td>
                <td>{t_g_n:+,}{t_p_n}</td>
            </tr>
        </tbody>
    </table>
    """

    report_data = {
        "title": "Direct & Organic Acquisition Growth",
        "special_type": "comparison_report",
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
        "summary_table_html": summary_table_html,
        "json_data": {
            "labels": ["Active Users", "New Users"],
            "datasets": [
                {"label": "Before", "data": [total_active_before, total_new_before]},
                {"label": "After", "data": [total_active_after, total_new_after]}
            ]
        },
        "explanation": f"### Comparison Period\n"
                       f"**Before Period**: {before_start} to {before_end}\n"
                       f"**After Period**: {start_date} to {end_date}\n\n"
                       f"*Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                       f"### Column Definitions\n"
                       f"* **Landing Page**: The URL path where the user first entered the site.\n"
                       f"* **Active Users (Before/After)**: Total number of active users in each period.\n"
                       f"* **Growth (Active)**: The raw difference in active users between the two periods, with percentage change.\n"
                       f"* **New Users (Before/After)**: Total number of first-time users in each period.\n"
                       f"* **Growth (New)**: The raw difference in new users between the two periods, with percentage change.\n"
                       f"* **Eng. Rate (After)**: The engagement rate specifically for the 'After' period.\n\n"
                       f"### Methodology\n"
                       f"This report analyzes the top 250 landing pages from the 'After' period. "
                       f"It then matches these pages against the previous 'Before' period. "
                       f"A value of **0** or **(New)** indicates the page was not prominent in the previous period."
    }

    for landing_page, data in pages_data.items():
        active_before = data["before"]["activeUsers"]
        active_after = data["after"]["activeUsers"]
        new_before = data["before"]["newUsers"]
        new_after = data["after"]["newUsers"]
        
        # Calculate engagement rate safely
        sessions_after = data["after"]["sessions"]
        engaged_after = data["after"]["engaged"]
        rate_after = (engaged_after / sessions_after) if sessions_after > 0 else 0
        
        growth_active = active_after - active_before
        pct_active = f" ({((growth_active / active_before) * 100):+.1f}%)" if active_before > 0 else " (New)"
        
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

    report_data["rows"].sort(key=lambda x: int(x[2]), reverse=True)
    return report_data
