import os
import csv
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

##########################
# CONFIG
##########################
CATEGORIES_CSV = "categories_extracted.csv"  # Must exist from your previous step
FOUND_LINKS_TXT = "found_links.txt"          # We'll generate this file
# If your CSV has a different column name for category link (e.g., "category_url"), adjust below.

##########################
# HELPER: INIT LOCAL DRIVER
##########################
def init_driver():
    """Initialize and return a local Chrome WebDriver in headless mode."""
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")  # run without opening a visible browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)
    return driver

##########################
# HELPER: PAGINATION & LINK COLLECTION
##########################
def collect_all_links(driver, category_url):
    """
    Collect all recipe links from a category page by traversing pagination.
    Returns a set of unique URLs.
    """
    all_links = set()

    try:
        driver.get(category_url)
        # Wait up to 10s for the first set of recipe link elements to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.mntl-card-list-items"))
        )
    except Exception:
        print(f"Warning: No recipe links found or page not loaded for: {category_url}")
        return all_links  # return an empty set

    page_number = 1
    while True:
        # Collect the links on the current page
        links = driver.find_elements(By.CSS_SELECTOR, "a.mntl-card-list-items")
        for link in links:
            url = link.get_attribute("href")
            if url:
                all_links.add(url)

        print(f"  Page {page_number} -> {len(all_links)} total links so far for {category_url}")

        # Attempt to click on "Next" button (pagination)
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pagination__next"))
            )
            next_button.click()
            # Wait for staleness of old links to ensure new page loaded
            WebDriverWait(driver, 5).until(EC.staleness_of(links[0]))
            page_number += 1
        except Exception:
            print("  No more pages or cannot click Next. Collecting complete.")
            break

    return all_links

##########################
# MAIN: PHASE 1
##########################
def main():
    """
    Phase 1: Read category URLs from `categories_extracted.csv`,
    open each category in a headless Chrome, gather recipe links, 
    and write them to `found_links.txt`.
    
    Format in `found_links.txt`: 
        categoryName|recipeURL
    """
    if not os.path.isfile(CATEGORIES_CSV):
        print(f"ERROR: '{CATEGORIES_CSV}' does not exist. Please provide the correct file.")
        return

    # Read categories from CSV.
    # We expect at least a column named "category_link". 
    # If you also have a "category_name" column, that's ideal for labeling.
    df = pd.read_csv(CATEGORIES_CSV)
    if "category_link" not in df.columns:
        print(f"ERROR: The file '{CATEGORIES_CSV}' must have a column named 'category_link'.")
        return

    # If you have a separate 'category_name' column, use that; otherwise we'll guess from the URL.
    has_cat_name_col = ("category_name" in df.columns)

    # Initialize headless Chrome once for all categories
    driver = init_driver()
    total_links_found = 0

    # We'll store lines, then write them at the end.
    lines_to_write = []

    for idx, row in df.iterrows():
        cat_url = str(row["category_link"]).strip()
        if not cat_url.startswith("http"):
            continue

        # Category name
        if has_cat_name_col:
            cat_name = str(row["category_name"]).strip()
        else:
            # fallback: parse from last path segment
            from urllib.parse import urlparse
            segments = [s for s in urlparse(cat_url).path.split("/") if s]
            cat_name = segments[-1] if segments else "unknown_category"

        print(f"\nCollecting links from category '{cat_name}' => {cat_url}")
        category_links = collect_all_links(driver, cat_url)
        print(f"Found {len(category_links)} total recipe links for category '{cat_name}'")

        for link in category_links:
            lines_to_write.append(f"{cat_name}|{link}")
        total_links_found += len(category_links)

    # Done collecting
    driver.quit()

    # Write found links to "found_links.txt"
    with open(FOUND_LINKS_TXT, "w", encoding="utf-8") as outfile:
        for line in lines_to_write:
            outfile.write(line + "\n")

    print(f"\nPHASE 1 COMPLETE: Wrote {total_links_found} total recipe links to '{FOUND_LINKS_TXT}'.")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total runtime: {end_time - start_time:.2f} seconds")
