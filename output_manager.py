import csv
import os
import time
import re
import datetime
import json

def _sanitize_name(name):
    """Converts a string to a sanitized, hyphenated, lowercase format for filenames/directories."""
    name = name.lower()
    # Replace one or more dots, whitespace, or other non-alphanumeric characters with a single hyphen
    name = re.sub(r'[^a-z0-9]+', '-', name)
    # Remove any leading/trailing hyphens
    name = name.strip('-')
    return name

def _format_value(value):
    """Tries to format a value as an integer with commas, otherwise returns the original value."""
    try:
        # Convert to float first to handle string representations of numbers like "1234.0"
        return f"{int(float(value)):,}"
    except (ValueError, TypeError):
        return value

def _generate_table_html(headers, rows, sticky_first_col=False):
    """Generates an HTML table string from headers and rows, with number formatting."""
    
    # Format numbers in rows
    formatted_rows = []
    for row in rows:
        formatted_rows.append([_format_value(cell) for cell in row])
        
    header_html = ""
    for i, header in enumerate(headers):
        cls = ' class="sticky-col"' if i == 0 and sticky_first_col else ""
        header_html += f'<th{cls}>{header}</th>'

    rows_html = ""
    for row in formatted_rows:
        rows_html += '<tr>'
        for i, cell in enumerate(row):
            cls = ' class="sticky-col"' if i == 0 and sticky_first_col else ""
            # If it's a sticky column, we also add fw-bold for consistency with other reports
            final_cls = cls if i != 0 or not sticky_first_col else ' class="sticky-col fw-bold"'
            rows_html += f'<td{final_cls}>{cell}</td>'
        rows_html += '</tr>'

    table_html = f"""
    <table id="reportTable" class="table table-striped table-bordered">
        <thead>
            <tr>
                {header_html}
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    return table_html

def _markdown_to_html(text):
    """A simple markdown to HTML converter for the explanation text."""
    if not text:
        return ""
    
    lines = text.strip().split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Convert bold syntax (**text**) to <strong>text</strong>
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)

        # Handle headers (e.g., ### Header)
        header_match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if header_match:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            level = len(header_match.group(1))
            header_text = header_match.group(2)
            html_lines.append(f'<h{level}>{header_text}</h{level}>')
            continue

        if line.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<p>{line}</p>')
            
    if in_list:
        html_lines.append('</ul>')
        
    return ''.join(html_lines)

def print_to_console(report_data, selected_property_info=None, start_date=None, end_date=None): # Match signature
    """Prints the report data in a formatted table to the console."""
    if not report_data or not report_data.get("rows"):
        print("No data to display.")
        return

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    title = report_data.get("title", "Report")
    date_range_str = report_data.get("date_range", "")

    # Format numbers for display
    formatted_rows = []
    for row in rows:
        formatted_rows.append([_format_value(cell) for cell in row])

    print(f"\n--- {title} ---")
    if selected_property_info:
        print(f"--- Property: {selected_property_info['display_name']} ({selected_property_info['property_id']}) ---")
    if date_range_str:
        print(f"--- Date Range: {date_range_str} ---")


    # Calculate column widths using formatted rows
    col_widths = [len(h) for h in headers]
    for row in formatted_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths) and len(str(cell)) > col_widths[i]:
                col_widths[i] = len(str(cell)) 

    # Print headers
    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    print(header_line)
    print("-" * len(header_line))

    # Print formatted rows
    for row in formatted_rows:
        row_line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        print(row_line)
    
    print("-" * len(header_line))

    explanation = report_data.get("explanation")
    if explanation:
        print(f"\n{explanation}")

def save_to_csv(report_data, selected_property_info, start_date, end_date):
    """Saves the report data to a CSV file in a property-specific subdirectory within 'output'."""
    if not report_data or not report_data.get("rows"):
        print("No data to save.")
        return
    if not selected_property_info or not start_date or not end_date:
        print("Error: Property information or date range missing for CSV output.")
        return

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    report_title = report_data.get("title", "report")
    
    # Sanitize names according to user preferences
    sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
    sanitized_report_title = _sanitize_name(report_title)

    # Create property-specific directory
    property_output_dir = os.path.join("output", sanitized_property_name)
    os.makedirs(property_output_dir, exist_ok=True) # Create if not exists

    filename = f"{sanitized_report_title}-{start_date}-to-{end_date}.csv"
    filepath = os.path.join(property_output_dir, filename)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Successfully saved report to {filepath}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")


def _save_historical_report_to_html(report_data, property_info, start_date, end_date):
    """Saves a historical report to an HTML file."""
    if not property_info or 'display_name' not in property_info or 'property_id' not in property_info:
        print("Error: Property information is incomplete. Cannot save HTML report.")
        return

    property_name = property_info['display_name']
    property_id = property_info['property_id']
    title = report_data.get('title', 'GA4 Report')
    
    # Sanitize property_name for filename
    sanitized_property_name = "".join(c for c in property_name if c.isalnum() or c in (' ', '_')).rstrip()
    
    filename = f"{title.replace(' ', '_')}_{sanitized_property_name}_{start_date}_to_{end_date}.html"
    
    # Ensure the 'output' directory exists
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)

    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('historical_report_template.html')
        
        html_content = template.render(
            title=title,
            property_name=property_name,
            property_id=property_id,
            date_range=report_data.get('date_range', f'{start_date} to {end_date}'),
            table_data=report_data.get('table_data', {}),
            chart_data=report_data.get('chart_data', {}),
            months=report_data.get('months', []),
            incomplete_months=report_data.get('incomplete_months', {}),
            explanation=report_data.get('explanation', '')
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Report successfully saved to: {filepath}")

    except ImportError:
        print("Jinja2 is not installed. Please install it using: pip install Jinja2")
    except Exception as e:
        print(f"An error occurred while generating the HTML report: {e}")


def save_to_html(report_data, selected_property_info, start_date, end_date):
    """Saves the report data to an HTML file in a property-specific subdirectory within 'output'."""
    if 'table_data' in report_data and 'chart_data' in report_data:
        _save_historical_report_to_html(report_data, selected_property_info, start_date, end_date)
        return

    # Specialized AI Traffic Acquisition Report
    if report_data.get("special_type") == "ai_traffic_acquisition_report":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        filename = f"ai-traffic-acquisition-report-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('ai-traffic-acquisition-report-template.html')
            
            # Calculate totals for AI Traffic
            total_total_users = 0
            total_active_users = 0
            total_sessions = 0
            total_engaged_sessions = 0
            total_conversions = 0
            unique_agents = set()

            for row in report_data.get("rows", []):
                if row[0]:
                    unique_agents.add(row[0].strip().lower())
                try:
                    total_total_users += int(float(row[2]))
                except (ValueError, TypeError):
                    pass
                try:
                    total_active_users += int(float(row[3]))
                except (ValueError, TypeError):
                    pass
                try:
                    total_sessions += int(float(row[4]))
                except (ValueError, TypeError):
                    pass
                try:
                    total_engaged_sessions += int(float(row[5]))
                except (ValueError, TypeError):
                    pass
                try:
                    total_conversions += int(float(row[7]))
                except (ValueError, TypeError):
                    pass

            total_engagement_rate = 0.0
            if total_sessions > 0:
                total_engagement_rate = (total_engaged_sessions / total_sessions) * 100

            total_ai_agents = len(unique_agents)
            explanation_html = _markdown_to_html(report_data.get("explanation", ""))
            
            # Format numbers for rows and totals
            formatted_rows = []
            for row in report_data.get("rows", []):
                formatted_rows.append([_format_value(cell) for cell in row])
                
            formatted_total_users = f"{total_total_users:,}"
            formatted_active_users = f"{total_active_users:,}"
            formatted_sessions = f"{total_sessions:,}"
            formatted_engaged_sessions = f"{total_engaged_sessions:,}"
            formatted_conversions = f"{total_conversions:,}"
            formatted_engagement_rate = f"{total_engagement_rate:.2f}%"

            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                headers=report_data.get("headers"),
                rows=formatted_rows,
                explanation_html=explanation_html,
                total_ai_agents=total_ai_agents,
                total_total_users=formatted_total_users,
                total_active_users=formatted_active_users,
                total_sessions=formatted_sessions,
                total_engaged_sessions=formatted_engaged_sessions,
                total_engagement_rate=formatted_engagement_rate,
                total_conversions=formatted_conversions,
                now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized AI report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report for AI: {e}. Falling back to standard format.")

    # Specialized All Properties AI Traffic Report
    if report_data.get("special_type") == "all_properties_ai_traffic_report":
        property_output_dir = os.path.join("output", "account")
        os.makedirs(property_output_dir, exist_ok=True)
        
        filename = f"all-properties-ai-traffic-report-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('all-properties-ai-traffic-report-template.html')
            
            headers = report_data.get("headers", [])
            rows = report_data.get("rows", [])
            
            # Extract AI agent names (middle columns of headers, excluding 'Property' and 'Total')
            ai_agents = headers[1:-1]
            
            # Calculate column totals (footers) and track AI agent totals
            footer_row = []
            max_agent_sum = -1
            top_agent_name = "-"
            ai_agent_totals = []
            
            # Calculate total for each AI agent column
            for i in range(1, len(headers) - 1):
                col_sum = 0
                for row in rows:
                    try:
                        col_sum += int(row[i])
                    except (ValueError, TypeError, IndexError):
                        pass
                footer_row.append(f"{col_sum:,}")
                ai_agent_totals.append((headers[i], col_sum))
                if col_sum > max_agent_sum:
                    max_agent_sum = col_sum
                    top_agent_name = headers[i]
                
            # Calculate overall total (last column)
            overall_total = 0
            for row in rows:
                try:
                    overall_total += int(row[-1])
                except (ValueError, TypeError, IndexError):
                    pass
            footer_row.append(f"{overall_total:,}")
            
            # Metrics for KPI cards
            total_properties = len(rows)
            total_ai_agents = len(ai_agents)
            total_active_users = f"{overall_total:,}"
            top_agent_value = max(0, max_agent_sum)
                    
            # Find top Property dynamically by scanning all rows
            top_property_name = "-"
            top_property_value = 0
            for row in rows:
                try:
                    row_total = int(row[-1])
                    if row_total > top_property_value:
                        top_property_value = row_total
                        top_property_name = row[0]
                except (ValueError, TypeError, IndexError):
                    pass
            
            # Format row values for rendering
            formatted_rows = []
            for row in rows:
                formatted_row = [row[0]]
                for val in row[1:]:
                    formatted_row.append(f"{val:,}")
                formatted_rows.append(formatted_row)
                
            explanation_html = _markdown_to_html(report_data.get("explanation", ""))
            
            # Sort AI sources by total active users descending, then alphabetically by name
            ai_agent_totals_sorted = sorted(ai_agent_totals, key=lambda x: (-x[1], x[0].lower()))
            formatted_ai_source_totals = []
            for agent, total in ai_agent_totals_sorted:
                formatted_ai_source_totals.append({
                    "source": agent,
                    "total_users": f"{total:,}"
                })

            html_content = template.render(
                report_title=report_data.get("title"),
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                headers=headers,
                rows=formatted_rows,
                footer_row=footer_row,
                total_properties=total_properties,
                total_ai_agents=total_ai_agents,
                total_active_users=total_active_users,
                top_agent_name=top_agent_name,
                top_agent_value=f"{top_agent_value:,}",
                top_property_name=top_property_name,
                top_property_value=f"{top_property_value:,}",
                ai_source_totals=formatted_ai_source_totals,
                explanation_html=explanation_html,
                now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized all properties report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized all properties HTML report: {e}. Falling back to standard format.")

    # Specialized Trend Report with Charting
    if report_data.get("special_type") == "channel_trend":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        filename = f"channel-performance-trends-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('channel_trend_template.html')
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                channels=report_data.get("channels"),
                months=report_data.get("months"),
                json_data=json.dumps(report_data.get("json_data"))
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized trend report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report: {e}. Falling back to standard format.")

    # Specialized Top Channels Comparison Report
    if report_data.get("special_type") == "top_channels_trend":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        filename = f"top-channels-comparison-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('top_channels_trend_template.html')
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                channels=report_data.get("channels"),
                months=report_data.get("months"),
                json_data=json.dumps(report_data.get("json_data"))
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized top channels report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report: {e}. Falling back to standard format.")

    # Specialized Hostname Trend Report
    if report_data.get("special_type") == "hostname-traffic-trend":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        filename = f"hostname-traffic-trend-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('hostname-trend-template.html')
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                hostnames=report_data.get("hostnames"),
                months=report_data.get("months"),
                json_data=json.dumps(report_data.get("json_data")),
                explanation=report_data.get("explanation")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized hostname trend report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report: {e}. Falling back to standard format.")

    # Specialized Hostname Top Comparison Report
    if report_data.get("special_type") == "hostname-top-comparison":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        filename = f"hostname-top-comparison-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('top-hostnames-comparison-template.html')
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                hostnames=report_data.get("hostnames"),
                months=report_data.get("months"),
                json_data=json.dumps(report_data.get("json_data")),
                explanation=report_data.get("explanation")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized hostname top comparison report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report: {e}. Falling back to standard format.")

    # Specialized Hostname Daily Comparison Report
    if report_data.get("special_type") == "hostname-daily-comparison":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        filename = f"hostname-daily-comparison-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('hostname-daily-comparison-template.html')
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                hostnames=report_data.get("hostnames"),
                dates=report_data.get("dates"),
                json_data=json.dumps(report_data.get("json_data")),
                explanation=report_data.get("explanation")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized daily hostname comparison report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report: {e}. Falling back to standard format.")

    # Specialized Top Campaign Daily Trend Report
    if report_data.get("special_type") == "top_campaign_daily_trend":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        report_title = report_data.get("title", "Top Campaign Daily Trend")
        sanitized_report_title = _sanitize_name(report_title)
        filename = f"{sanitized_report_title}-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('top_campaign_daily_trend_template.html')
            
            # Convert explanation from Markdown to HTML
            explanation = report_data.get("explanation", "")
            explanation_html = _markdown_to_html(explanation)
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                campaign_names=report_data.get("campaign_names"),
                dates=report_data.get("dates"),
                json_data=json.dumps(report_data.get("json_data")),
                explanation_html=explanation_html,
                now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized daily trend report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized HTML report: {e}. Falling back to standard format.")

    # Specialized Channel Traffic by Hour Report
    if report_data.get("special_type") == "channel_traffic_by_hour":
        ...
    # Specialized Comparison Report with Summary and Chart
    if report_data.get("special_type") == "comparison_report":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        report_title = report_data.get("title", "Comparison Report")
        sanitized_report_title = _sanitize_name(report_title)
        filename = f"{sanitized_report_title}-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('comparison_report_template.html')
            
            explanation_html = _markdown_to_html(report_data.get("explanation", ""))
            summary_table_html = report_data.get("summary_table_html", "")
            table_html = _generate_table_html(report_data.get("headers"), report_data.get("rows"))

            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                json_data=json.dumps(report_data.get("json_data")),
                explanation_html=explanation_html,
                summary_table_html=summary_table_html,
                table_html=table_html
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized comparison report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized comparison HTML report: {e}. Falling back to standard format.")

    # Specialized Top Campaign Daily Trend (used for Countries too)
    if report_data.get("special_type") == "top_campaign_daily_trend":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        report_title = report_data.get("title", "Daily Trend")
        sanitized_report_title = _sanitize_name(report_title)
        filename = f"{sanitized_report_title}-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('top_campaign_daily_trend_template.html')
            
            explanation_html = _markdown_to_html(report_data.get("explanation", ""))
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                date_range=f"{start_date} to {end_date}",
                campaign_names=report_data.get("campaign_names"),
                dates=report_data.get("dates"),
                json_data=json.dumps(report_data.get("json_data")),
                explanation_html=explanation_html,
                now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized daily trend report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized daily trend HTML report: {e}. Falling back to standard format.")

    # Specialized Monthly Traffic Source Report
    if report_data.get("special_type") == "monthly_traffic_source_report":
        sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
        property_output_dir = os.path.join("output", sanitized_property_name)
        os.makedirs(property_output_dir, exist_ok=True)
        
        report_title = report_data.get("title", "Monthly Traffic Source Trend")
        sanitized_report_title = _sanitize_name(report_title)
        filename = f"{sanitized_report_title}-{start_date}-to-{end_date}.html"
        filepath = os.path.join(property_output_dir, filename)
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('monthly_traffic_source_template.html')
            
            explanation_html = _markdown_to_html(report_data.get("explanation", ""))
            
            html_content = template.render(
                report_title=report_data.get("title"),
                property_display_name=selected_property_info['display_name'],
                property_id=selected_property_info['property_id'],
                date_range=report_data.get("date_range", f"{start_date} to {end_date}"),
                months_json=json.dumps(report_data.get("months")),
                m_data_json=json.dumps(report_data.get("m_data")),
                sm_data_json=json.dumps(report_data.get("sm_data")),
                sm_keys_json=json.dumps(report_data.get("sm_keys")),
                m_keys=report_data.get("m_keys"),
                sm_keys=report_data.get("sm_keys"),
                explanation_html=explanation_html,
                now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Successfully saved specialized monthly traffic source report to {filepath}")
            return
        except Exception as e:
            print(f"Error generating specialized monthly traffic source HTML report: {e}. Falling back to standard format.")

    if not report_data or not report_data.get("rows"):
        print("No data to save.")
        return
    if not selected_property_info or not start_date or not end_date:
        print("Error: Property information or date range missing for HTML output.")
        return

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    report_title = report_data.get("title", "Report")

    # Sanitize names according to user preferences
    sanitized_property_name = _sanitize_name(selected_property_info['display_name'])
    sanitized_report_title = _sanitize_name(report_title)

    # Create property-specific directory
    property_output_dir = os.path.join("output", sanitized_property_name)
    os.makedirs(property_output_dir, exist_ok=True) # Create if not exists

    filename = f"{sanitized_report_title}-{start_date}-to-{end_date}.html"
    filepath = os.path.join(property_output_dir, filename)

    # Load HTML template
    template_path = os.path.join(os.path.dirname(__file__), "templates", "html-report-template.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: HTML template not found at {template_path}")
        return
    except Exception as e:
        print(f"Error loading HTML template: {e}")
        return

    # Generate table HTML
    table_html = _generate_table_html(headers, rows)

    # Convert explanation from Markdown to HTML
    explanation = report_data.get("explanation", "")
    explanation_html = _markdown_to_html(explanation)

    # Replace placeholders
    date_range_str = report_data.get("date_range", f"{start_date} to {end_date}")
    html_content = html_content.replace("{{ report_title }}", report_title)
    html_content = html_content.replace("{{ property_display_name }}", selected_property_info['display_name'])
    html_content = html_content.replace("{{ date_range }}", date_range_str)
    html_content = html_content.replace("<!-- REPORT_TABLE_PLACEHOLDER -->", table_html)
    html_content = html_content.replace("<!-- REPORT_EXPLANATION_PLACEHOLDER -->", explanation_html)

    try:
        with open(filepath, "w", encoding="utf-8") as htmlfile:
            htmlfile.write(html_content)
        print(f"Successfully saved report to {filepath}")
    except Exception as e:
        print(f"Error saving HTML file: {e}")

def save_to_csv_and_html(report_data, selected_property_info, start_date, end_date):
    """Saves the report data to both CSV and HTML files."""
    save_to_csv(report_data, selected_property_info, start_date, end_date)
    save_to_html(report_data, selected_property_info, start_date, end_date)

def save_report_to_file(report_data, filename):
    """Saves a formatted report to a single text file in the 'output' directory."""
    if not report_data or not report_data.get("rows"):
        print(f"  -> No data to save for {filename}.")
        return

    # Ensure output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    title = report_data.get("title", "Report")
    date_range_str = report_data.get("date_range", "")

    # Format numbers for display
    formatted_rows = []
    for row in rows:
        formatted_rows.append([_format_value(cell) for cell in row])

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in formatted_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths) and len(str(cell)) > col_widths[i]:
                col_widths[i] = len(str(cell))

    # Build the report string
    report_string = []
    report_string.append(f"--- {title} ---")
    if date_range_str:
        report_string.append(f"--- Date Range: {date_range_str} ---")
    report_string.append("\n")

    # Header line
    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    report_string.append(header_line)
    report_string.append("-" * len(header_line))

    # Row lines
    for row in formatted_rows:
        row_line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        report_string.append(row_line)
    
    report_string.append("-" * len(header_line))

    explanation = report_data.get("explanation")
    if explanation:
        report_string.append(f"\n{explanation}")

    # Write to file
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(report_string))
    except Exception as e:
        print(f"  -> Error saving text file: {e}")
