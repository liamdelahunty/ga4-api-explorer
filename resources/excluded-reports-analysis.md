# Excluded GA4 Reports Analysis

This document provides a comprehensive audit of the Google Analytics 4 (GA4) report modules that are not included in the automated scripts [run_last_month_reports.py](file:///home/liamvictor/projects/ga4-api-explorer/run_last_month_reports.py) or [run_trend_reports.py](file:///home/liamvictor/projects/ga4-api-explorer/run_trend_reports.py).

It outlines which reports are covered by other modules, why they are not considered essential for standard monthly or historical trend analysis, and the specific scenarios in which they become useful.

---

## Summary Matrix

Below is a quick-reference table of the 25 excluded report modules:

| Report Module | Covered by Another Report? | Primary Reason for Exclusion | Best Running Frequency / Use Case |
| :--- | :--- | :--- | :--- |
| `channel_traffic_by_hour_report` | No | Highly tactical hour-of-day data; changes slowly. | Ad-hoc (ad scheduling/social posts). |
| `cohort_retention_report` | No | Overly complex retention metrics; better for product analytics. | Ad-hoc (measuring product-market fit). |
| `country_daily_traffic_report` | No | Daily data is too noisy for high-level summaries. | Ad-hoc (detecting local outages or viral spikes). |
| `country_traffic_by_hour_report` | No | Hourly international data is too granular. | Ad-hoc (timezone-specific scheduling). |
| `direct_organic_pages_report` | Partially | Specific comparison of Direct vs Organic traffic. | Ad-hoc (PPC stoppage impact audits). |
| `file_downloads_report` | No | Monitors event interaction clicks rather than overall traffic. | Monthly/Ad-hoc (resource performance tracking). |
| `high_engagement_pages_report` | Partially | Filtered subset of top pages; not a full trend view. | Ad-hoc (content audit and optimisation). |
| `hostname-daily-comparison` | No | Internal hostname validation; changes rarely. | Ad-hoc (security audits / spam detection). |
| `hostname-top-comparison` | No | Interactive tool for subdomain trends. | Ad-hoc (subdomain launch reviews). |
| `hostname-traffic-trend` | No | Hostname-level trend; not property growth. | Ad-hoc (multisite performance tracking). |
| `landing_pages_report` | Partially | Captured by broader page-view reports. | Monthly (conversion rate optimization). |
| `lead_quality_by_channel_report` | Yes | Redundant with `channel_trend_report`. | Ad-hoc (detailed conversion auditing). |
| `low_engagement_pages_report` | Partially | Audit sheet for pages with poor engagement. | Ad-hoc (UX and content redesign planning). |
| `new_vs_returning_by_channel_report` | Partially | Ratios are stable; overall numbers covered. | Ad-hoc (loyalty campaign assessments). |
| `new_vs_returning_engagement_report` | Partially | Engagement differences change slowly. | Ad-hoc (long-term brand affinity metrics). |
| `outbound_clicks_report` | No | Exit-focused metric rather than acquisition. | Ad-hoc (affiliate / external outbound tracking). |
| `screen_size_engagement_report` | Partially | Tech specifications change very slowly. | Ad-hoc (responsive layout audits). |
| `session_source_medium_report` | Yes | Redundant with `traffic_acquisition_report`. | Ad-hoc (quick source debug). |
| `top_campaign_daily_trend_report` | No | Daily granularity is too noisy for monthly views. | Ad-hoc (active PPC campaign monitoring). |
| `top_channels_trend_report` | Yes | Replaced by custom `channel_trend_report`. | Ad-hoc (programmatic historical queries). |
| `top_cities_report` | No | City traffic shifts slowly; too granular for strategy. | Ad-hoc (geotargeted marketing campaigns). |
| `top_numeric_campaigns_daily_report`| No | Daily tracking of numeric campaigns. | Ad-hoc (UTM tracking code validations). |
| `user_technology_report` | Yes | Replaced by `device_type` reports. | Ad-hoc (browser compatibility testing). |
| `utm_campaign_report` | No | Only relevant if active campaigns are running. | Monthly (PPC / newsletter performance review). |
| `utm_full_content_report` | No | Specialized sanitised UTM landing page report. | Monthly (marketing campaign path attribution). |

---

## Detailed Report Breakdown

### Traffic by Hour & Day Granularity

#### `channel_traffic_by_hour_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: Hourly traffic is extremely granular and fluctuates based on timezone differences. It is a tactical optimization metric rather than a high-level growth trend.
* **When it is useful**: Useful when determining when to schedule marketing emails, publish blog posts, or run time-sensitive social media campaigns to match peak visitor hours.

#### `country_traffic_by_hour_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: Combining country and hour-of-day metrics creates a very high-dimensional table that does not aid in general performance reporting.
* **When it is useful**: Useful for global brands wanting to identify timezone-specific peaks per country to schedule regional marketing pushes.

#### `country_daily_traffic_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: Daily granularity is too noisy for high-level monthly summaries. Standard country traffic changes slowly enough that monthly snapshots are sufficient.
* **When it is useful**: Useful to diagnose immediate issues, such as detecting localized regional network outages or measuring the immediate impact of a viral marketing campaign in a specific country.

---

### User Cohorts & Loyalty

#### `cohort_retention_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: Cohort retention requires complex multi-week tracking. For standard monthly reporting, basic active user trends are a cleaner metric of growth/decline.
* **When it is useful**: Essential for product managers evaluating SaaS platforms or subscription services to measure product-market fit and user churn rates over weeks and months.

#### `new_vs_returning_by_channel_report.py`
* **Covered by another report?** Partially. Overall user volume differences are covered by [traffic_acquisition_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/traffic_acquisition_report.py) (which shows total vs new users).
* **Why it isn't essential**: The ratio of new vs returning visitors by channel tends to remain stable month-over-month.
* **When it is useful**: Useful when evaluating remarketing campaigns or loyalty programmes designed to bring previous users back via specific channels (like email).

#### `new_vs_returning_engagement_report.py`
* **Covered by another report?** Partially. Overall engagement is tracked in the main reports.
* **Why it isn't essential**: Loyalty and engagement comparison is a long-term strategic metric that does not change quickly enough to warrant regular monthly tracking.
* **When it is useful**: Useful when auditing site usability or content appeal to see if returning visitors remain active longer than first-time search arrivals.

---

### Hostname Validation & Security

#### `hostname-daily-comparison.py`, `hostname-top-comparison.py`, `hostname-traffic-trend.py`
* **Covered by another report?** No.
* **Why they aren't essential**: Hostnames should ideally remain constant (e.g. your primary domain and subdomains). These scripts do not measure business growth or shrinkage.
* **When they are useful**: Critical for security audits, diagnosing referral spam, verifying that tracking tags are not being hijacked on external sites, or confirming when a new landing page subdomain goes live.

---

### Page-Level & Conversion Auditing

#### `direct_organic_pages_report.py`
* **Covered by another report?** Partially. General page activity is covered by [top_pages_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/top_pages_report.py) and [landing_pages_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/landing_pages_report.py).
* **Why it isn't essential**: This is a highly specific comparative analysis of pages receiving organic search vs direct traffic.
* **When it is useful**: Extremely useful after stopping a paid search (PPC) campaign to see if direct/organic traffic began picking up the slack on specific entry pages.

#### `landing_pages_report.py`
* **Covered by another report?** Partially. General page views are captured in [top_pages_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/top_pages_report.py).
* **Why it isn't essential**: While landing pages are important, [top_pages_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/top_pages_report.py) is sufficient for a quick monthly summary of top content.
* **When it is useful**: Essential when running conversion rate optimisation (CRO) audits to see which entry points have the highest bounce rates.

#### `high_engagement_pages_report.py`
* **Covered by another report?** Partially. General traffic counts are in [top_pages_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/top_pages_report.py).
* **Why it isn't essential**: This is an optimization filter that isolates high-performing pages rather than displaying property growth.
* **When it is useful**: Useful when auditing content to find which articles or guides are most successful at holding user attention.

#### `low_engagement_pages_report.py`
* **Covered by another report?** Partially.
* **Why it isn't essential**: This is a tactical content auditing list rather than a general growth trend metric.
* **When it is useful**: Useful for SEO and UX teams when identifying pages that receive high traffic but fail to keep users engaged, suggesting misleading titles or poor user experience.

#### `lead_quality_by_channel_report.py`
* **Covered by another report?** Yes. Both [channel_trend_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/channel_trend_report.py) and [channel_overview_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/channel_overview_report.py) track leads and conversion rates per channel.
* **Why it isn't essential**: The data is redundant because lead counts and traffic conversions are already fully visualised in the primary channel trend and overview reports.
* **When it is useful**: Useful when you require a specific, isolated table strictly containing lead quality percentages without other traffic noise.

---

### Specialised Interaction Tracking

#### `file_downloads_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: File downloads are a micro-conversion metric. They do not represent overall site traffic growth or decline.
* **When it is useful**: Useful when you are running campaigns that push a specific downloadable asset (like a whitepaper, PDF guide, or software update) and want to track the download count over time.

#### `outbound_clicks_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: This tracks users *leaving* your site via external links. It is a loss metric rather than an acquisition metric.
* **When it is useful**: Critical when running affiliate marketing sites, tracking referrals sent to external partner portals, or monitoring clicks to social profiles.

---

### Device & Technology Specifics

#### `screen_size_engagement_report.py`
* **Covered by another report?** Partially. Overall device splits are covered by [device_type_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/device_type_report.py) and [device_type_historical_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/device_type_historical_report.py).
* **Why it isn't essential**: Screen sizes and resolutions change very slowly (over years, not months) and represent tech requirements rather than business growth.
* **When it is useful**: Useful for frontend developers and UI/UX designers to test mobile responsiveness and decide which screen breakpoints to optimise first.

#### `user_technology_report.py`
* **Covered by another report?** Yes. Completely covered by [device_type_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/device_type_report.py) and [device_type_historical_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/device_type_historical_report.py).
* **Why it isn't essential**: Operating systems and browser splits are tech support metrics that do not track business growth.
* **When it is useful**: Useful to frontend engineering teams to determine which browser versions (e.g. Chrome, Safari, Firefox) must be supported in the next release.

---

### Campaign & Marketing-Specific Reports

#### `top_campaign_daily_trend_report.py`, `top_numeric_campaigns_daily_report.py`
* **Covered by another report?** No.
* **Why they aren't essential**: Daily campaign tracking is highly volatile and noisy. For monthly/quarterly reports, campaign names are better tracked at a monthly aggregate level.
* **When they are useful**: Critical for paid search manager reviews during active campaign launches, validating budget spends, or checking for campaign tag issues.

#### `top_channels_trend_report.py`
* **Covered by another report?** Yes. Replaced by [channel_trend_report.py](file:///home/liamvictor/projects/ga4-api-explorer/reports/channel_trend_report.py), which pulls the same channel data but is formatted for the interactive charting template.
* **Why it isn't essential**: It is redundant with the custom HTML trend module.
* **When it is useful**: Useful for quick terminal/text-only historical queries of default channel groupings.

#### `top_cities_report.py`
* **Covered by another report?** No.
* **Why it isn't essential**: Demographic traffic shifts very slowly and is typically too granular for strategic monthly planning.
* **When it is useful**: Useful when planning localised advertising campaigns or reviewing physical store performance regions.

#### `utm_campaign_report.py`, `utm_full_content_report.py`
* **Covered by another report?** No.
* **Why they aren't essential**: These are marketing campaign specific reports. If you are not running active UTM-tagged advertising or newsletter distributions, these reports will return empty or irrelevant data.
* **When they are useful**: Useful during monthly marketing reviews to measure the return on investment (ROI) of paid advertising (Google Ads, Facebook Ads) or email newsletter campaigns.
