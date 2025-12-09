# GA4 API Explorer

This project provides an interactive command-line interface to explore and generate reports from the Google Analytics 4 (GA4) API.

It allows you to interactively select a GA4 property, choose from a list of available reports, and generate the output in your console or as a CSV or HTML file.

## Project Structure

-   `run_report.py`: The main entry point for the application. This script orchestrates the user interaction, report discovery, and output generation.
-   `ga4_client.py`: Handles all authentication and Google API client instantiation. It finds the `client_secret.json` file and creates the necessary clients for the Admin and Data APIs.
-   `output_manager.py`: Contains functions to format and save report data into different formats (Console, CSV, HTML).
-   `list_properties.py`: A utility script to quickly list all accessible accounts and properties.
-   `/config`: This directory should contain your `client_secret.json` service account key file.
-   `/output`: The default directory where generated CSV and HTML reports are saved.
-   `/reports`: This directory contains all the available report modules. Each Python file in here is a self-contained report that can be discovered and run by `run_report.py`.

## Getting Started

### 1. Initial Setup

Follow the **[SETUP_GUIDE.md](SETUP_GUIDE.md)** to configure your Google Cloud project, create a service account, and download your `client_secret.json` key file.

### 2. Install Dependencies

It is highly recommended to use a Python virtual environment to keep your project dependencies isolated.

```bash
# Create a virtual environment (do this once)
py -m venv venv

# Activate the virtual environment
# On Windows (Git Bash):
source venv/Scripts/activate
# On Windows (PowerShell):
# .\venv\Scripts\activate

# Install the required libraries
pip install -r requirements.txt
```

### 3. Run the Interactive Reporter

Once your virtual environment is activated, run the main script:

```bash
py run_report.py
```

You will be guided through a series of interactive menus to:
1.  Select a GA4 property.
2.  Select an available report.
3.  Choose your desired output format (Console, CSV, or HTML).

The script will loop, allowing you to run multiple reports without restarting.

## How to Add a New Report

This project is designed to be easily extensible. To add a new report:

1.  Create a new Python file in the `/reports` directory (e.g., `my_new_report.py`).
2.  In that file, create a function named `run_report(property_id, data_client)`.
3.  Inside your function, use the `data_client` to build and run your `RunReportRequest`.
4.  Your function **must** return the data in a standardized dictionary format:

    ```python
    {
        "title": "My Awesome Report",
        "headers": ["Dimension 1", "Metric 1"],
        "rows": [
            ["Row 1 Dim", "Row 1 Met"],
            ["Row 2 Dim", "Row 2 Met"]
        ]
    }
    ```

That's it! The `run_report.py` script will automatically discover your new file and add it to the list of available reports.
