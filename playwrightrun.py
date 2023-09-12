import json
import os
import hashlib
import requests
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google.cloud import storage


# Initialize Google Cloud Storage
storage_client = storage.Client()
bucket_name = ""
bucket = storage_client.get_bucket(bucket_name)

# Slack webhook URL
slack_webhook_url = ""

# Read URLs from the JSON file in GCS
json_blob = bucket.blob("")
json_data = json_blob.download_as_text()
data = json.loads(json_data)
urls = data['urls']

total_urls = len(urls)
successful_scrapes = 0

# Initialize Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()

    for url in urls:
        # Create a new page
        page = browser.new_page()

        try:
            # Navigate to the URL
            page.goto(url)

            # Wait for the page to fully load, including JavaScript execution
            page.wait_for_load_state("networkidle")

            # Extract HTML content
            html_content = page.content()

            # Generate the current date and time
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            # Generate a hashed name for the file using the HTML content
            hashed_name = hashlib.md5(html_content.encode()).hexdigest()

            # Create directory structure: url > scrape date/time > hashed name for file
            directory_path = os.path.join(url.replace("https://", "").replace("http://", "").replace("/", "_"),
                                          current_datetime)

            # Full path for the file in GCS
            gcs_file_path = os.path.join(directory_path, f"{hashed_name}.html")

            # Upload the HTML content to Google Cloud Storage
            blob = bucket.blob(gcs_file_path)
            blob.upload_from_string(html_content, content_type='text/html')

            logging.info(f"Scraped {url} and saved to {gcs_file_path} in Google Cloud Storage")
            successful_scrapes += 1

        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")

        finally:
            # Close the page
            page.close()

    # Close the browser
    browser.close()

# Calculate and post the percentage of successful scrapes to Slack
if total_urls > 0:
    success_rate = (successful_scrapes / total_urls) * 100
    slack_message = {
        "text": f"Scraping completed. {success_rate}% of URLs were successfully scraped."
    }
    requests.post(slack_webhook_url, json=slack_message)
    logging.info(f"Scraping completed. {success_rate}% of URLs were successfully scraped.")
