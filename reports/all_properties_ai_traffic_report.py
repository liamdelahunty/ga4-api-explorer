import json
import os
import ga4_client
from google.analytics.admin_v1alpha.types import ListPropertiesRequest
from reports.ai_traffic_acquisition_report import run_report as run_single_ai_report

def get_properties():
    # Attempt to load from properties cache
    cache_filepath = os.path.join("cache", "properties_cache.json")
    if os.path.exists(cache_filepath):
        try:
            with open(cache_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    # Fallback to Admin API call
    admin_client = ga4_client.get_admin_client()
    if not admin_client:
        return []
    try:
        all_accounts = list(admin_client.list_accounts())
        properties = []
        for account in all_accounts:
            request = ListPropertiesRequest(filter=f"ancestor:{account.name}")
            account_properties = list(admin_client.list_properties(request=request))
            for prop in account_properties:
                properties.append({
                    "display_name": prop.display_name,
                    "property_id": prop.name.split('/')[-1]
                })
        return properties
    except Exception as e:
        print(f"Error fetching properties from GA4 API: {e}")
        return []

def run_report(property_id, data_client, start_date, end_date):
    """
    Runs an AI Traffic Acquisition Collation report across all properties.
    Note: The first parameter (property_id) is ignored as we query all properties.
    """
    properties = get_properties()
    if not properties:
        print("No properties found to run the collation report on.")
        return None

    # Collect unique AI agents and property-agent values
    ai_agents = set()
    property_data = {}  # property_id -> {display_name, agents: {agent -> active_users}}

    for prop in properties:
        p_id = prop["property_id"]
        p_name = prop["display_name"]
        
        print(f"Querying AI traffic for property: {p_name} ({p_id})...")
        
        # We query the single property report
        single_report = run_single_ai_report(p_id, data_client, start_date, end_date)
        if not single_report or not single_report.get("rows"):
            continue

        property_data[p_id] = {
            "display_name": p_name,
            "agents": {}
        }

        for row in single_report["rows"]:
            agent_source = row[0]
            active_users = 0
            try:
                active_users = int(float(row[3])) # index 3 is activeUsers
            except (ValueError, TypeError):
                pass

            if agent_source not in property_data[p_id]["agents"]:
                property_data[p_id]["agents"][agent_source] = 0
            property_data[p_id]["agents"][agent_source] += active_users
            ai_agents.add(agent_source)

    if not property_data:
        # Return empty structure
        return {
            "title": "All Properties AI Traffic Collation",
            "special_type": "all_properties_ai_traffic_report",
            "headers": ["Property", "Total"],
            "rows": [],
            "explanation": "No AI traffic detected for any property in the selected date range."
        }

    # Sort AI agents columns alphabetically
    sorted_agents = sorted(ai_agents)

    # Calculate total AI traffic for each property to sort properties descending
    prop_totals = {}
    for p_id, p_info in property_data.items():
        prop_totals[p_id] = sum(p_info["agents"].values())

    sorted_properties = sorted(property_data.keys(), key=lambda p_id: prop_totals[p_id], reverse=True)

    # Construct headers: ["Property", ...sorted_agents, "Total"]
    headers = ["Property"] + sorted_agents + ["Total"]

    # Construct rows: [property_name, agent1_users, agent2_users, ..., property_total]
    rows = []
    for p_id in sorted_properties:
        p_info = property_data[p_id]
        row = [p_info["display_name"]]
        for agent in sorted_agents:
            val = p_info["agents"].get(agent, 0)
            row.append(val)
        row.append(prop_totals[p_id])
        rows.append(row)

    report_data = {
        "title": "All Properties AI Traffic Collation",
        "special_type": "all_properties_ai_traffic_report",
        "headers": headers,
        "rows": rows,
        "explanation": (
            "This report collates AI traffic (Active Users) across all GA4 properties. "
            "It displays a grid comparing properties with the AI discovery tools driving traffic to them."
        )
    }

    return report_data
