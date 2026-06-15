# Guide to Implementing a Google Search Console (GSC) Monitoring System

This document outlines the approach to create a monitoring report for Google Search Console properties, mirroring the functionality and structure of the existing GA4 weekly monitoring report. This will enable proactive detection of significant changes in search performance.

## 1. Goal

Develop a Python script (within your GSC project) to:
*   Leverage your existing robust GSC API suite to fetch key GSC metrics.
*   Compare current week's data against Last Week, Last Month, and Last Year baselines.
*   Present data in an HTML report using a traffic light system to highlight significant changes.
*   Provide flexibility in data granularity (e.g., aggregate, by Query, by Page).

## 2. Key Differences and Considerations for GSC

While the overall report structure and comparison logic can largely follow the GA4 report, several GSC-specific aspects need attention. Your existing GSC API suite should handle most of the API client and authentication setup.

### 2.1. API & Authentication

*   **API Client:** Leverage your existing GSC API client setup.
*   **Authentication:** Your existing GSC project's authentication methods should be used. Ensure the underlying service account (if used) has appropriate GSC scopes (e.g., `https://www.googleapis.com/auth/webmasters.readonly`).

### 2.2. Metrics and Dimensions

*   **GSC Metrics to Prioritise:**
    *   `clicks`: Number of clicks from Google Search results.
    *   `impressions`: Number of times your URL appeared in Google Search results.
    *   `ctr`: Click-through rate (clicks / impressions).
    *   `position`: Average position of your URL in search results.
*   **GSC Dimensions for Granular Breakdown:**
    *   `query`: Search queries that led to your site (highly recommended for detail table, analogous to Source/Medium).
    *   `page`: Specific pages on your site that appeared in search results (useful for page-level performance monitoring).
    *   Other dimensions like `country` or `device` can also be considered based on reporting needs.
*   **Date Range:** GSC API supports `startDate` and `endDate` parameters, similar to GA4. The date range calculation logic from the GA4 report should be adapted directly.
*   **Aggregation:** GSC API responses will need careful handling to sum up rows for aggregate totals. For `position`, remember it's an average, so direct summation isn't appropriate for its aggregate, it needs to be an average of averages or a weighted average.

### 2.3. Properties

*   **GSC Property ID:** GSC properties are identified by their `siteUrl` (e.g., `sc-domain:example.com`, `https://www.example.com/`). A JSON configuration file (e.g., `config/gsc_properties.json` within your GSC project) will need to store these GSC-specific IDs.

## 3. Report Structure

The GSC monitoring report should closely mirror the GA4 report for consistency and ease of understanding.

*   **HTML Template:** The structure and styling of the `templates/canary_report_template.html` from *this* project should be used as a direct reference and adapted for GSC-specific data fields.
*   **Global Aggregate Table:** A top-level table summarizing all GSC properties with key metrics (`clicks`, `impressions`, `ctr`, `position`) for Current, Last Week, Last Month, and Last Year periods. Include actual numbers, percentage changes, and the traffic light system.
*   **Individual Property Details:** For each GSC property:
    *   Its own `<h2>` heading.
    *   Detailed tables breaking down metrics by chosen dimensions (e.g., `query` or `page`).
    *   The traffic light system will apply only to the aggregate overview, not to granular rows.
*   **Date Period Table:** A table detailing the exact date ranges for Current, Last Week, Last Month, Last Year.
*   **Command Line Info & Instructions:** Display the command used to generate the report and instructions for switching granularity/dimensions.
*   **Colour Scheme Legend:** Explanation of the traffic light system.
*   **HTML Output:** Generate a single, dated HTML file in the `output/` directory of your GSC project.

## 4. Proposed Development Prompt for Your GSC Project

---

**Prompt:**

"**Goal:** Implement a new Python script, `reports/monitoring/gsc_canary_html.py`, to generate a weekly monitoring report for Google Search Console (GSC) properties.

**Leverage Existing GSC API Suite:** Utilize the GSC API client and authentication already set up within this project. Assume you have helper functions available to make GSC API calls (e.g., `get_gsc_data(siteUrl, start_date, end_date, metrics, dimensions)`).

**Functionality:**
1.  **Property Configuration:** Read GSC properties from a JSON configuration file specified by a `--config` flag (e.g., `config/gsc_properties.json`). Each entry should have a `name` and `siteUrl`.
2.  **Metrics to Track:** Focus on `clicks`, `impressions`, `ctr`, and `position`. For `position`, ensure calculations for averages are handled correctly, as GSC returns it as an average, not a sum.
3.  **Date Ranges:** Implement the same date range logic as found in the GA4 report (`weekly_canary_html.py` from the GA4-API-Explorer project) for Current, Last Week, Last Month, and Last Year, ensuring day-of-week alignment for 'Last Year'.
4.  **Granularity:**
    *   Implement a `--dimension` flag (e.g., `query`, `page`) for detailed breakdowns. Default to `None` if no dimension is specified, meaning the detailed table will be aggregate-only. If `query` is chosen, normalize query strings (e.g., lowercasing, trimming).
    *   Implement a separate flag, `--aggregate-only`, to generate a report with *only* the global aggregate table and no per-property detail tables (even if a `--dimension` is specified).
5.  **Report Structure (HTML):**
    *   Create a new template: `templates/gsc_canary_report_template.html`.
    *   **Crucially, use the `templates/canary_report_template.html` from the GA4-API-Explorer project as a direct structural and styling guide.** Adapt this template to display GSC-specific metrics (`clicks`, `impressions`, `ctr`, `position`) instead of `newUsers`. Maintain the overall layout (top sections, global aggregate table, per-property detail).
    *   **Global Aggregate Table:** At the top, list all GSC properties with their aggregate `clicks`, `impressions`, `ctr`, and `position` for each period (Current, Last Week, Last Month, Last Year), including actual numbers, percentage changes, and the traffic light system.
    *   **Per-Property Detail (Conditional):** If `--aggregate-only` is not used, for each property, display detailed tables by the chosen `--dimension` (Query or Page), showing the current metrics and historical comparisons.
6.  **Traffic Light System:** Apply the same traffic light logic (Red, Amber, Light Green, Dark Green, No Colour) to the percentage changes in both the global aggregate table and per-property detail tables. Adapt the ranges and meaning if necessary for `position` (where lower is better).
7.  **Output:** Generate a dated HTML file in the `output/` directory (e.g., `output/gsc-monitoring-report-YYYY-MM-DD-dimension_value.html` or `output/gsc-monitoring-report-YYYY-MM-DD-aggregate-only.html`).
8.  **Usability Enhancements:** Include command-line invocation details, instructions for switching granularity/dimensions, and the colour scheme legend, similar to the GA4 report.
9.  **GSC Specifics:** Remember that `position` is an average, so calculating percentage change might need careful interpretation (e.g., a positive change in position means a *worse* position, so traffic light logic might need to be inverted for this metric). For `CTR`, it's already a percentage, so percentage change of CTR will be percentage point change. Ensure numbers are comma-separated.

---
