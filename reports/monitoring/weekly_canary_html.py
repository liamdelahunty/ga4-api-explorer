import argparse
import json
import datetime
import sys
import os
from dateutil.relativedelta import relativedelta

# Add the project root to the path so we can import modules from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from jinja2 import Template
from ga4_client import get_data_client
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

def get_status_class(change_percent):
    if change_percent is None: return ""
    
    if change_percent <= -25:
        return "red"
    elif change_percent <= -10:
        return "amber"
    elif change_percent >= 25:
        return "positive-strong-green"
    elif change_percent >= 10:
        return "positive-moderate-green"
    else: # Between -10 and +10 (exclusive of -10 and +10)
        return "" # No color for this range

def calculate_change(current, historical):
    if not historical or historical == 0: return None
    return round(((current - historical) / historical) * 100, 1)

def normalize_source_medium(source_medium_name):
    """
    Normalizes source/medium names to handle capitalization and consolidate email variations.
    """
    normalized_name = source_medium_name.lower().strip()

    # Consolidate common email variations
    if 'email' in normalized_name or 'mail' in normalized_name:
        return 'email / email' # Standardize all email to 'email / email'

    return normalized_name

def group_referral_sources(sources_list):
    """Aggregates all 'referral' sources into a single 'referral' entry."""
    grouped_sources = {}
    referral_users = 0
    
    for s in sources_list:
        # Heuristic: if medium contains 'referral', group it
        if 'referral' in s['name'].lower(): 
            referral_users += s['users']
        else:
            grouped_sources[s['name']] = grouped_sources.get(s['name'], 0) + s['users']
            
    if referral_users > 0:
        grouped_sources['(referral)'] = referral_users
        
    # Convert back to list of dicts
    return [{"name": name, "users": users} for name, users in grouped_sources.items()]


def get_aggregate_new_users(client, property_id, start_date, end_date):
    """Fetches total newUsers for a given property and period."""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="newUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    
    response = client.run_report(request=request)
    if response.rows:
        return int(response.rows[0].metric_values[0].value)
    return 0

def get_data_for_period(client, property_id, start_date, end_date, granularity="source_medium"):
    """Fetches newUsers and source/medium for a given property and period."""
    dimension_name = "sessionSourceMedium" if granularity == "source_medium" else "sessionMedium"

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=dimension_name)],
        metrics=[Metric(name="newUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    
    response = client.run_report(request=request)
    
    total_users = 0
    sources = []
    
    for row in response.rows:
        users = int(row.metric_values[0].value)
        # Normalize the dimension value here
        normalized_name = normalize_source_medium(row.dimension_values[0].value)
        
        total_users += users
        sources.append({
            "name": normalized_name,
            "users": users
        })
    
    # Group referral sources before returning
    processed_sources = group_referral_sources(sources)
    return total_users, processed_sources

def run_report(property_list, granularity="source_medium"):
    print(f"Generating weekly canary report for {len(property_list)} properties...")
    client = get_data_client()
    today = datetime.date.today()
    
    sites_data = []
    
    for prop in property_list:
        # Date ranges (last 7 days, matched to day-of-week)
        curr_start = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        curr_end = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Last week (the 7 days prior to the current week)
        prev_w_start = (today - datetime.timedelta(days=14)).strftime('%Y-%m-%d')
        prev_w_end = (today - datetime.timedelta(days=8)).strftime('%Y-%m-%d')
        
        # Last month (roughly 28 days prior, matching day of week)
        prev_m_start = (today - datetime.timedelta(days=35)).strftime('%Y-%m-%d')
        prev_m_end = (today - datetime.timedelta(days=29)).strftime('%Y-%m-%d')
        
        curr_start_date_obj = today - datetime.timedelta(days=7)
        target_weekday = curr_start_date_obj.weekday() # 0=Mon, 6=Sun

        approx_last_year_start = curr_start_date_obj + relativedelta(years=-1)
        prev_y_start_date_obj = approx_last_year_start
        while prev_y_start_date_obj.weekday() != target_weekday:
            prev_y_start_date_obj += datetime.timedelta(days=1)
        
        prev_y_end_date_obj = prev_y_start_date_obj + datetime.timedelta(days=6)
        
        prev_y_start = prev_y_start_date_obj.strftime('%Y-%m-%d')
        prev_y_end = prev_y_end_date_obj.strftime('%Y-%m-%d')

        curr_total_aggregate = get_aggregate_new_users(client, prop['property_id'], curr_start, curr_end)
        prev_w_total_aggregate = get_aggregate_new_users(client, prop['property_id'], prev_w_start, prev_w_end)
        prev_m_total_aggregate = get_aggregate_new_users(client, prop['property_id'], prev_m_start, prev_m_end)
        prev_y_total_aggregate = get_aggregate_new_users(client, prop['property_id'], prev_y_start, prev_y_end)

        # Calculate changes for aggregate (now using the specific aggregate totals)
        w_change_aggregate = calculate_change(curr_total_aggregate, prev_w_total_aggregate)
        m_change_aggregate = calculate_change(curr_total_aggregate, prev_m_total_aggregate)
        y_change_aggregate = calculate_change(curr_total_aggregate, prev_y_total_aggregate)
        
        # Fetch granular data for the detailed table
        _, curr_sources_raw = get_data_for_period(client, prop['property_id'], curr_start, curr_end, granularity)
        _, prev_w_sources_raw = get_data_for_period(client, prop['property_id'], prev_w_start, prev_w_end, granularity)
        _, prev_m_sources_raw = get_data_for_period(client, prop['property_id'], prev_m_start, prev_m_end, granularity)
        _, prev_y_sources_raw = get_data_for_period(client, prop['property_id'], prev_y_start, prev_y_end, granularity)
        
        # Build site data
        site = {
            "name": prop['name'],
            # The top-level 'current_users' is now the aggregate, not sum of sources
            "current_users": f"{curr_total_aggregate:,}", 
            "aggregate_status": get_status_class(w_change_aggregate), # Use week aggregate for overall status
            "aggregate_status_text": "Normal" if get_status_class(w_change_aggregate) == "green" else "Check",
            
            "curr_total_aggregate": f"{curr_total_aggregate:,}",
            "prev_w_total_aggregate": f"{prev_w_total_aggregate:,}",
            "w_change_aggregate": f"{w_change_aggregate:,}" if w_change_aggregate is not None else "N/A",
            "w_status_aggregate": get_status_class(w_change_aggregate),
            
            "prev_m_total_aggregate": f"{prev_m_total_aggregate:,}",
            "m_change_aggregate": f"{m_change_aggregate:,}" if m_change_aggregate is not None else "N/A",
            "m_status_aggregate": get_status_class(m_change_aggregate),

            "prev_y_total_aggregate": f"{prev_y_total_aggregate:,}",
            "y_change_aggregate": f"{y_change_aggregate:,}" if y_change_aggregate is not None else "N/A",
            "y_status_aggregate": get_status_class(y_change_aggregate),

            "sources": []
        }
        
        # Process individual sources
        prev_w_sources_map = {s['name']: s['users'] for s in prev_w_sources_raw}
        prev_m_sources_map = {s['name']: s['users'] for s in prev_m_sources_raw}
        prev_y_sources_map = {s['name']: s['users'] for s in prev_y_sources_raw}

        for s in curr_sources_raw:
            source_name = s['name']
            current_users = s['users']
            
            week_historical_users = prev_w_sources_map.get(source_name, 0)
            month_historical_users = prev_m_sources_map.get(source_name, 0)
            year_historical_users = prev_y_sources_map.get(source_name, 0)
            
            week_change = calculate_change(current_users, week_historical_users)
            month_change = calculate_change(current_users, month_historical_users)
            year_change = calculate_change(current_users, year_historical_users)
            
            site["sources"].append({
                "name": source_name,
                "current_users": f"{current_users:,}",
                "week_users": f"{week_historical_users:,}",
                "week_change": f"{week_change:,}" if week_change is not None else "N/A",
                "month_users": f"{month_historical_users:,}",
                "month_change": f"{month_change:,}" if month_change is not None else "N/A",
                "year_users": f"{year_historical_users:,}",
                "year_change": f"{year_change:,}" if year_change is not None else "N/A",
            })
        
        sites_data.append(site)
        
    # Render HTML
    with open('templates/canary_report_template.html', 'r') as f:
        template = Template(f.read())
    
    current_period_date_range = f"{curr_start} to {curr_end}"
        
    # Capture the command line used to run the report
    full_command = " ".join(sys.argv)

    html_out = template.render(
        report_date=today.strftime("%Y-%m-%d"), 
        current_period_date_range=current_period_date_range,
        sites=sites_data,
        invoked_command=full_command,
        current_granularity=granularity,
        curr_period=f"{curr_start} to {curr_end}",
        prev_w_period=f"{prev_w_start} to {prev_w_end}",
        prev_m_period=f"{prev_m_start} to {prev_m_end}",
        prev_y_period=f"{prev_y_start} to {prev_y_end}"
    )
    
    filename = f"output/monitoring-report-{today.strftime('%Y-%m-%d')}-{granularity}.html"
    with open(filename, 'w') as f:
        f.write(html_out)
        
    print(f"Report generated: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run weekly canary report.")
    parser.add_argument("--config", required=True, help="Path to properties config JSON file.")
    parser.add_argument("--source", action="store_true", 
                        help="Include source details in traffic breakdown (defaults to medium-level).")
    args = parser.parse_args()
    
    granularity = "source_medium" if args.source else "medium"
    
    with open(args.config, 'r') as f:
        data = json.load(f)
        
    run_report(data['properties'], granularity)
