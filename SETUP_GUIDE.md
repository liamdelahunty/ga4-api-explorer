# GA4 API Explorer Setup Guide

This guide will walk you through the process of setting up the necessary credentials to use the Google Analytics 4 (GA4) API.

## 1. Enable the Google Analytics Data API

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Select your project from the project dropdown menu at the top of the page, or create a new one if you don't have one already.
3.  In the navigation menu, go to **APIs & Services > Enabled APIs & services**.
4.  Click on **+ ENABLE APIS AND SERVICES**.
5.  Search for "Google Analytics Data API" and "Google Analytics Admin API".
6.  Enable both APIs for your project.

## 2. Create a Service Account

A service account is a special type of Google account intended to represent a non-human user that needs to authenticate and be authorized to access data in Google APIs.

1.  In the Google Cloud Console, navigate to **IAM & Admin > Service Accounts**.
2.  Click **+ CREATE SERVICE ACCOUNT**.
3.  Fill in the service account details:
    *   **Service account name:** A descriptive name, e.g., "ga4-api-explorer".
    *   **Service account ID:** This will be automatically generated based on the name.
    *   **Description:** A brief description of what this service account will be used for.
4.  Click **CREATE AND CONTINUE**.
5.  **Grant this service account access to the project** by adding the "Viewer" role. This allows the service account to see the GA4 properties within the project.
6.  Click **CONTINUE**.
7.  You can skip the "Grant users access to this service account" step for now. Click **DONE**.

## 3. Grant Service Account Access to GA4 Property

You now need to grant the newly created service account access to your Google Analytics 4 property.

1.  Go to your [Google Analytics](https://analytics.google.com/) account.
2.  Navigate to the **Admin** section of your GA4 property.
3.  In the "Property" column, click on **Property Access Management**.
4.  Click the **+** button to add a new user.
5.  In the "Email address" field, paste the email address of the service account you created in the previous step (you can find this in the "Service Accounts" section of the Google Cloud Console).
6.  Select the desired permissions. "Viewer" is sufficient for reading data.
7.  Click **Add**.

## 4. Generate a JSON Key File

The JSON key file is a secure file that contains the credentials for your service account.

1.  In the Google Cloud Console, go to **IAM & Admin > Service Accounts**.
2.  Click on the email address of the service account you created.
3.  Go to the **KEYS** tab.
4.  Click **ADD KEY > Create new key**.
5.  Select **JSON** as the key type and click **CREATE**.
6.  A JSON file will be downloaded to your computer. **Treat this file like a password and keep it secure.**

## 5. Set Up Your Local Environment

1.  Move the downloaded JSON file into the `config` directory of this project. It's a good practice to rename it to something simple, like `client_secret.json`.
2.  Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the **full, absolute path** of this JSON file.

    *   **Windows (Command Prompt):**
        ```cmd
        set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\project\ga4-api-explorer\config\client_secret.json"
        ```

    *   **Windows (PowerShell):**
        ```powershell
        $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\project\ga4-api-explorer\config\client_secret.json"
        ```

    *   **macOS / Linux (Bash/Zsh):**
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/project/ga4-api-explorer/config/client_secret.json"
        ```

    **Important:** Replace `"C:\path\to\your\project"` or `"/path/to/your/project"` with the actual absolute path to your `ga4-api-explorer` directory.

    To make this setting permanent, you can add this command to your shell's startup file (e.g., `.bash_profile`, `.zshrc`, or by using the Environment Variables system settings on Windows).

You are now ready to run the Python scripts in this project to interact with the GA4 API.
