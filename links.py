# import time
# from collections import deque
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

# def scrape_all_recipe_links(
#     start_url="https://www.simplyrecipes.com/recipes/",
#     output_file="recipe_links.txt"
# ):
#     # 1. Set up Selenium using webdriver_manager so we don't need a manual chromedriver path
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service)
#     driver.maximize_window()

#     visited = set()  # Keep track of visited URLs
#     found_links = set()  # All unique “/recipes/” links
#     queue = deque([start_url])

#     while queue:
#         current_url = queue.popleft()
#         if current_url in visited:
#             continue

#         visited.add(current_url)
#         print(f"Visiting: {current_url}")

#         try:
#             driver.get(current_url)
#             time.sleep(2)  # Adjust sleep as needed to allow the page to load

#             # 2. Find all links containing '/recipes/'
#             anchors = driver.find_elements(By.XPATH, "//a[contains(@href, '/recipes/')]")
#             for a in anchors:
#                 href = a.get_attribute("href")
#                 if href and "/recipes/" in href:
#                     found_links.add(href)
#                     if href not in visited:
#                         queue.append(href)

#         except Exception as e:
#             print(f"Error loading {current_url}: {e}")

#     # 3. Save results to a text file
#     with open(output_file, "w", encoding="utf-8") as f:
#         for link in sorted(found_links):
#             f.write(link + "\n")

#     print(f"\nDone! Found {len(found_links)} unique links containing '/recipes/'.")
#     print(f"All links saved to {output_file}.")

#     # Close the browser
#     driver.quit()

# if __name__ == "__main__":
#     scrape_all_recipe_links()



import csv

# A simple dictionary mapping your domain names to their base URLs
DOMAIN_TO_BASEURL = {
    "BBC Good Food": "https://www.bbcgoodfood.com",
    # Add other mappings here if needed, e.g.:
    # "NYT Cooking": "https://cooking.nytimes.com",
    # "Epicurious": "https://www.epicurious.com",
    # etc.
}

def transform_path(old_path: str) -> str:
    """
    Converts '/recipes/collection/...' to '/recipes/category/...'
    or any other transformations you need.
    """
    return old_path.replace("/recipes/collection/", "/recipes/category/")

def convert_to_full_url(domain_label: str, path: str) -> str:
    """
    1. Map the domain label to an actual base URL.
    2. Transform '/recipes/collection/' to '/recipes/category/'.
    3. Combine into a complete URL.
    """
    base_url = DOMAIN_TO_BASEURL.get(domain_label.strip(), "")
    if not base_url:
        # If we don't recognize the domain label, either return the original path or skip it
        return path  # or return ""

    new_path = transform_path(path.strip())
    return base_url + new_path

def process_csv(
    input_csv="output.csv",
    output_csv="output_links.csv"
):
    """
    Reads each row of input_links.csv, which is assumed to have:
       domain_label,path
    Then transforms it to a full URL, and writes to output_links.csv.
    """
    with open(input_csv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin)
        rows = list(reader)

    converted_urls = []
    for row in rows:
        if len(row) < 2:
            # Skip rows that don't have at least two columns
            continue

        domain_label, raw_path = row[0], row[1]
        full_url = convert_to_full_url(domain_label, raw_path)
        converted_urls.append(full_url)

    # Write the final URLs to an output CSV (one per line)
    with open(output_csv, "w", encoding="utf-8", newline="") as fout:
        writer = csv.writer(fout)
        for url in converted_urls:
            writer.writerow([url])

    print(f"Processed {len(converted_urls)} lines.")
    print(f"Results saved to '{output_csv}'.")

if __name__ == "__main__":
    process_csv()






# import csv

# # 1) Define your domain mapping (website -> base URL).
# DOMAIN_MAP = {
#     "BBC Good Food": "https://www.bbcgoodfood.com",
#     "Bon Appétit": "https://www.bonappetit.com",
#     "Taste of Home": "https://www.tasteofhome.com",
#     "Simply Recipes": "https://www.simplyrecipes.com",
#     "The Kitchn": "https://www.thekitchn.com",
#     "Food.com": "https://www.food.com",
#     "NY Times Cooking": "https://cooking.nytimes.com",
#     "Cookpad": "https://cookpad.com",
#     "Yummly": "https://www.yummly.com",
#     "Serious Eats": "https://www.seriouseats.com",
#     "Delish": "https://www.delish.com",
#     "EatingWell": "https://www.eatingwell.com",
#     "Jamie Oliver": "https://www.jamieoliver.com",
#     # Add more if needed...
# }

# def ensure_full_url(website: str, category_link: str) -> str:
#     """
#     If category_link starts with 'http' or 'https', return it as is.
#     Otherwise, prepend the domain from DOMAIN_MAP (if present).
#     """
#     link = category_link.strip()
#     if link.startswith("http://") or link.startswith("https://"):
#         return link

#     base_url = DOMAIN_MAP.get(website.strip())
#     if not base_url:
#         # If we don't have a domain mapping, return unchanged or handle as needed
#         return link

#     # Join base_url and partial path
#     # Remove trailing slash on base_url, remove leading slash on link
#     return base_url.rstrip("/") + "/" + link.lstrip("/")

# def fill_in_full_links(
#     input_csv="/Users/gowthamsolleti/Downloads/actor-allrecipes-scraper-master/all_recipe_categories.csv",
#     output_csv="output.csv"
# ):
#     """
#     Reads website, category_link from input_csv.
#     If category_link isn't a full URL, it prepends the correct domain.
#     Writes the updated data to output_csv.
#     """
#     with open(input_csv, "r", encoding="utf-8") as fin:
#         reader = csv.reader(fin)
#         rows = list(reader)

#     updated_rows = []
#     for row in rows:
#         if len(row) < 2:
#             # In case of malformed line, skip or handle as needed
#             continue
#         website, category_link = row[0].strip(), row[1].strip()
#         full_url = ensure_full_url(website, category_link)
#         updated_rows.append([website, full_url])

#     # Write to output
#     with open(output_csv, "w", encoding="utf-8", newline="") as fout:
#         writer = csv.writer(fout)
#         writer.writerows(updated_rows)

#     print(f"Done! Processed {len(updated_rows)} rows.")
#     print(f"Results saved to '{output_csv}'.")

# if __name__ == "__main__":
#     fill_in_full_links()
