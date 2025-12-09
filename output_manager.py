import csv
import os
import time

def print_to_console(report_data):
    """Prints the report data in a formatted table to the console."""
    if not report_data or not report_data.get("rows"):
        print("No data to display.")
        return

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    title = report_data.get("title", "Report")

    print(f"\n--- {title} ---")

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if len(str(cell)) > col_widths[i]:
                col_widths[i] = len(str(cell)) 

    # Print headers
    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        row_line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        print(row_line)
    
    print("-" * len(header_line))

def save_to_csv(report_data):
    """Saves the report data to a CSV file in the 'output' directory."""
    if not report_data or not report_data.get("rows"):
        print("No data to save.")
        return

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    title = report_data.get("title", "report").replace(" ", "_").lower()
    
    filename = f"{title}_{{time.strftime('%Y%m%d-%H%M%S')}}.csv"
    filepath = os.path.join("output", filename)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Successfully saved report to {filepath}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")


def save_to_html(report_data):
    """Saves the report data to an HTML file in the 'output' directory."""
    if not report_data or not report_data.get("rows"):
        print("No data to save.")
        return

    headers = report_data.get("headers", [])
    rows = report_data.get("rows", [])
    title = report_data.get("title", "Report")

    filename = f"{title.replace(' ', '_').lower()}_{{time.strftime('%Y%m%d-%H%M%S')}}.html"
    filepath = os.path.join("output", filename)

    # Basic but clean HTML structure
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: sans-serif; }}
            table {{ border-collapse: collapse; width: 80%; margin: 20px auto; }}
            th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            h1 {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <thead>
                <tr>
                    {''.join(f'<th>{header}</th>' for header in headers)}
                </tr>
            </thead>
            <tbody>
                {''.join(f'<tr>{"".join(f"<td>{cell}</td>" for cell in row)}</tr>' for row in rows)}
            </tbody>
        </table>
    </body>
    </html>
    """

    try:
        with open(filepath, "w", encoding="utf-8") as htmlfile:
            htmlfile.write(html_content)
        print(f"Successfully saved report to {filepath}")
    except Exception as e:
        print(f"Error saving HTML file: {e}")
