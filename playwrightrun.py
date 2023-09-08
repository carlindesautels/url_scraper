import json
import os
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Load URLs from the JSON file
with open('urls.json', 'r') as f:
    data = json.load(f)
    urls = data['urls']

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

            # Optional: Parse the HTML using BeautifulSoup (if needed)
            soup = BeautifulSoup(html_content, 'html.parser')

            # Generate the current date and time
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            # Generate a hashed name for the file
            hashed_name = hashlib.md5(html_content.encode()).hexdigest()

            # Create directory structure: url > scrape date/time > hashed name for file
            directory_path = os.path.join(url.replace("https://", "").replace("http://", "").replace("/", "_"),
                                          current_datetime)
            os.makedirs(directory_path, exist_ok=True)

            # Save the HTML content to an HTML file
            output_file_path = os.path.join(directory_path, f"{hashed_name}.html")
            with open(output_file_path, 'w', encoding='utf-8') as f_out:
                f_out.write(html_content)

            print(f"Scraped {url} and saved to {output_file_path}")

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

        finally:
            # Close the page
            page.close()

    # Close the browser
    browser.close()
