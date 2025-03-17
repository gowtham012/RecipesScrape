# # import csv
# # import json
# # import requests
# # from bs4 import BeautifulSoup
# # from urllib.parse import urljoin, urlparse
# # import sys
# # import time

# # def clean_json_ld_text(text):
# #     """Remove HTML comment markers and extra whitespace."""
# #     if not text:
# #         return text
# #     text = text.strip()
# #     if text.startswith("<!--"):
# #         text = text.replace("<!--", "")
# #     if text.endswith("-->"):
# #         text = text.replace("-->", "")
# #     return text.strip()

# # def find_recipe_object(data):
# #     """
# #     Recursively search through data for an object that contains
# #     both 'recipeIngredient' and 'recipeInstructions'.
# #     """
# #     if isinstance(data, dict):
# #         if "recipeIngredient" in data and "recipeInstructions" in data:
# #             return data
# #         for key, value in data.items():
# #             recipe = find_recipe_object(value)
# #             if recipe:
# #                 return recipe
# #     elif isinstance(data, list):
# #         for item in data:
# #             recipe = find_recipe_object(item)
# #             if recipe:
# #                 return recipe
# #     return None

# # def extract_json_ld(soup):
# #     """Extract JSON-LD data from the page and try to find the recipe object."""
# #     scripts = soup.find_all("script", type="application/ld+json")
# #     for script in scripts:
# #         text = script.string
# #         if not text:
# #             continue
# #         text = clean_json_ld_text(text)
# #         try:
# #             data = json.loads(text)
# #         except Exception:
# #             continue

# #         # Try: if data has an "@graph", look for an item with @type "Recipe"
# #         if isinstance(data, dict) and "@graph" in data:
# #             for item in data["@graph"]:
# #                 if isinstance(item, dict) and item.get("@type") == "Recipe":
# #                     return item

# #         # If data is a list, check each element.
# #         if isinstance(data, list):
# #             for item in data:
# #                 if isinstance(item, dict) and item.get("@type") == "Recipe":
# #                     return item

# #         # Finally, do a recursive search for an object with recipe markers.
# #         recipe_obj = find_recipe_object(data)
# #         if recipe_obj:
# #             return recipe_obj

# #     return None

# # def scrape_recipe(url):
# #     """Scrape an individual recipe given its URL."""
# #     result = {"url": url}
# #     parsed = urlparse(url)
# #     host = parsed.netloc.lower()
# #     if host.startswith("www."):
# #         host = host[4:]
# #     result["host"] = host

# #     headers = {"User-Agent": "Mozilla/5.0 (compatible; RecipeScraperBot/1.0)"}
# #     try:
# #         resp = requests.get(url, headers=headers)
# #     except Exception as e:
# #         print(f"Error fetching {url}: {e}")
# #         return None

# #     if resp.status_code != 200:
# #         print(f"Failed to fetch {url}")
# #         return None

# #     soup = BeautifulSoup(resp.text, "html.parser")
# #     json_ld = extract_json_ld(soup)

# #     if json_ld:
# #         result["title"] = json_ld.get("name", "")
# #         author = json_ld.get("author", "")
# #         if isinstance(author, dict):
# #             result["author"] = author.get("name", "")
# #         elif isinstance(author, list):
# #             result["author"] = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in author)
# #         else:
# #             result["author"] = author

# #         result["description"] = json_ld.get("description", "")
# #         result["image"] = json_ld.get("image", "")
# #         result["ingredients"] = json_ld.get("recipeIngredient", [])

# #         instructions = json_ld.get("recipeInstructions", "")
# #         if isinstance(instructions, list):
# #             steps = []
# #             for item in instructions:
# #                 if isinstance(item, dict):
# #                     steps.append(item.get("text", ""))
# #                 else:
# #                     steps.append(str(item))
# #             result["instructions_list"] = steps
# #             result["instructions"] = "\n".join(steps)
# #         elif isinstance(instructions, str):
# #             result["instructions_list"] = [instructions]
# #             result["instructions"] = instructions
# #         else:
# #             result["instructions_list"] = []
# #             result["instructions"] = ""

# #         result["cook_time"] = json_ld.get("cookTime", "")
# #         result["prep_time"] = json_ld.get("prepTime", "")
# #         result["total_time"] = json_ld.get("totalTime", "")
# #         result["servings"] = json_ld.get("recipeYield", "")
# #         result["nutrients"] = json_ld.get("nutrition", {})

# #         ratings = None
# #         if "aggregateRating" in json_ld:
# #             agg = json_ld["aggregateRating"]
# #             if isinstance(agg, dict):
# #                 ratings = agg.get("ratingValue", None)
# #         result["ratings"] = ratings

# #         result["category"] = json_ld.get("recipeCategory", "")
# #         result["cuisine"] = json_ld.get("recipeCuisine", "")
# #         result["language"] = "en"
# #         result["site_name"] = host.capitalize()
# #     else:
# #         result["title"] = soup.title.string if soup.title else ""
# #         result["wild_mode"] = True

# #     return result

# # def flatten_value(value):
# #     """Convert lists or dictionaries to a string for CSV output."""
# #     if isinstance(value, list):
# #         return "; ".join(str(item) for item in value)
# #     elif isinstance(value, dict):
# #         return json.dumps(value)
# #     else:
# #         return value

# # def get_recipe_links(category_url):
# #     """
# #     Fetch a category page and extract recipe links.
# #     For King Arthur Baking, recipe URLs contain "/recipes/" 
# #     but we want to exclude those with "collections" in the URL.
# #     """
# #     headers = {"User-Agent": "Mozilla/5.0 (compatible; RecipeScraperBot/1.0)"}
# #     try:
# #         resp = requests.get(category_url, headers=headers)
# #     except Exception as e:
# #         print(f"Error fetching category {category_url}: {e}")
# #         return []
# #     if resp.status_code != 200:
# #         print(f"Failed to fetch category {category_url}")
# #         return []
# #     soup = BeautifulSoup(resp.text, "html.parser")
# #     links = set()
# #     for a in soup.find_all("a", href=True):
# #         href = a["href"]
# #         abs_url = urljoin(category_url, href)
# #         # Look for URLs that contain '/recipes/' but exclude 'collections'
# #         if "/recipes/" in abs_url and "collections" not in abs_url:
# #             links.add(abs_url)
# #     return list(links)

# # def scrape_category(category_url):
# #     """Extract all recipe links from a category page and scrape each recipe."""
# #     print(f"Processing category: {category_url}")
# #     recipe_links = get_recipe_links(category_url)
# #     print(f"Found {len(recipe_links)} recipe links in category {category_url}")
# #     recipes = []
# #     for link in recipe_links:
# #         print(f"Scraping recipe: {link}")
# #         recipe_data = scrape_recipe(link)
# #         if recipe_data:
# #             recipes.append(recipe_data)
# #         time.sleep(1)  # pause to be polite
# #     return recipes

# # if __name__ == "__main__":
# #     # For example, you can pass the category URL directly, or read from a CSV file.
# #     # Here, we'll hardcode the King Arthur Baking category URL for testing:
# #     category_url = "https://www.budgetbytes.com/category/recipes/cost-per-recipe/recipes-under-10/"
# #     all_recipes = scrape_category(category_url)

# #     # Write all scraped recipe data to a CSV file.
# #     output_csv = "all_recipes.csv"
# #     fieldnames = [
# #         "url", "host", "wild_mode", "title", "author", "description", "image",
# #         "ingredients", "instructions", "instructions_list", "cook_time", "prep_time",
# #         "total_time", "servings", "nutrients", "ratings", "category", "cuisine",
# #         "language", "site_name"
# #     ]
# #     with open(output_csv, "w", newline="", encoding="utf-8") as f:
# #         import csv
# #         writer = csv.DictWriter(f, fieldnames=fieldnames)
# #         writer.writeheader()
# #         for recipe in all_recipes:
# #             row = {key: flatten_value(recipe.get(key, "")) for key in fieldnames}
# #             writer.writerow(row)

# #     print(f"Scraped data for {len(all_recipes)} recipes saved to {output_csv}")


# # import csv
# # import requests
# # from bs4 import BeautifulSoup
# # from urllib.parse import urljoin, urlparse
# # import sys
# # import time

# # def get_recipe_links(category_url):
# #     """
# #     Fetch a category page and extract recipe links.
    
# #     Uses domain-specific filtering:
# #       - For pinchofyum.com: Recipe URLs are assumed to have exactly one non-empty path segment.
# #       - For budgetbytes.com: Recipe URLs are assumed to have exactly one path segment and do not include excluded keywords.
# #       - For others: Look for URLs that contain '/recipe/'.
# #     """
# #     headers = {"User-Agent": "Mozilla/5.0"}
# #     try:
# #         resp = requests.get(category_url, headers=headers)
# #     except Exception as e:
# #         print(f"Error fetching category {category_url}: {e}")
# #         return []
# #     if resp.status_code != 200:
# #         print(f"Failed to fetch category {category_url}")
# #         return []
    
# #     soup = BeautifulSoup(resp.text, "html.parser")
# #     links = set()
# #     parsed_cat = urlparse(category_url)
# #     cat_domain = parsed_cat.netloc.lower()

# #     for a in soup.find_all("a", href=True):
# #         abs_url = urljoin(category_url, a["href"])
# #         parsed = urlparse(abs_url)
# #         # Only consider links on the same domain as the category URL.
# #         if parsed.netloc.lower() != cat_domain:
# #             continue

# #         path = parsed.path.strip("/")
# #         segments = [seg for seg in path.split("/") if seg]

# #         # Domain-specific filtering:
# #         if "pinchofyum.com" in cat_domain:
# #             # Valid recipe URLs for Pinch of Yum usually have exactly one segment.
# #             if len(segments) == 1:
# #                 links.add(abs_url)
# #         elif "budgetbytes.com" in cat_domain:
# #             # Exclude links with unwanted keywords.
# #             exclude_keywords = ["category", "random", "about", "faq", "contact", "welcome", "index", "archive"]
# #             if any(keyword in parsed.path.lower() for keyword in exclude_keywords):
# #                 continue
# #             if len(segments) == 1:
# #                 links.add(abs_url)
# #         else:
# #             # For all other domains, assume recipe URLs contain '/recipe/'.
# #             if "/recipe/" in abs_url:
# #                 links.add(abs_url)
# #     return list(links)

# # if __name__ == "__main__":
# #     if len(sys.argv) < 2:
# #         print("Usage: python script.py <categories_csv_file>")
# #         sys.exit(1)

# #     # Read categories from CSV.
# #     # Expected CSV format: each row has at least two columns:
# #     # category_name, category_url
# #     csv_filename = sys.argv[1]
# #     categories = []  # list of tuples: (category_name, category_url)
# #     with open(csv_filename, newline='', encoding='utf-8') as csvfile:
# #         reader = csv.reader(csvfile)
# #         for row in reader:
# #             if len(row) >= 2:
# #                 category_name = row[0].strip()
# #                 category_url = row[1].strip()
# #                 if category_url.startswith("http"):
# #                     categories.append((category_name, category_url))

# #     all_recipe_links = []
# #     for cat_name, cat_url in categories:
# #         print(f"Processing category: {cat_name} - {cat_url}")
# #         recipe_links = get_recipe_links(cat_url)
# #         print(f"Found {len(recipe_links)} recipe links in category {cat_name}")
# #         for link in recipe_links:
# #             all_recipe_links.append({
# #                 "category_name": cat_name,
# #                 "category_url": cat_url,
# #                 "recipe_url": link
# #             })
# #         time.sleep(2)  # be polite between category requests

# #     # Write all collected recipe links to a CSV file.
# #     output_csv = "recipe_links.csv"
# #     with open(output_csv, "w", newline="", encoding="utf-8") as f:
# #         fieldnames = ["category_name", "category_url", "recipe_url"]
# #         writer = csv.DictWriter(f, fieldnames=fieldnames)
# #         writer.writeheader()
# #         for row in all_recipe_links:
# #             writer.writerow(row)

# #     print(f"Extracted recipe links saved to {output_csv}")




# import csv
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import sys
# import time
# import re
# def extract_category_from_url(url):
#     """
#     Extracts a category from a URL if it contains "/tag/".
#     For example, from "https://www.budgetbytes.com/tag/celery/" it returns "celery".
#     Otherwise, returns an empty string.
#     """
#     parsed = urlparse(url)
#     path = parsed.path.lower()
#     if "/tag/" in path:
#         # Split at "/tag/" and take the next segment
#         parts = path.split("/tag/")
#         if len(parts) > 1:
#             # Split the remaining part by "/" and take the first segment.
#             return parts[1].split("/")[0]
#     return ""

# def get_recipe_links(category_url):
#     """
#     Fetch a category page and extract recipe links using domain‐specific filtering.
    
#     The function applies different heuristics based on the domain:
#       - pinchofyum.com: Recipe URLs are assumed to have exactly one non‐empty path segment.
#       - budgetbytes.com: Excludes links with common non-recipe keywords and expects a single-segment slug.
#       - smittenkitchen.com: Assumes recipe URLs contain a date pattern at the start (e.g. /2010/05/).
#       - simplyrecipes.com: Includes links whose path contains "recipes-" or "/recipes/".
#       - minimalistbaker.com: Excludes known non-recipe paths (like "about", "shop", etc.) and includes URLs whose last segment contains a hyphen.
#       - halfbakedharvest.com: Only includes links that contain "/recipes/".
#       - joythebaker.com: Assumes recipe URLs include a date (e.g. /2024/03/).
#       - foodiecrush.com: Includes links that contain "/recipes/".
#       - kingarthurbaking.com: Excludes common non-recipe keywords (like "collections", "shop", etc.) and includes links with a hyphen.
#       - food52.com: Includes links containing "/recipes/".
#       - Fallback: If the URL contains either "/recipe/" or "/recipes/", include it.
#     """
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         resp = requests.get(category_url, headers=headers)
#     except Exception as e:
#         print(f"Error fetching category {category_url}: {e}")
#         return []
#     if resp.status_code != 200:
#         print(f"Failed to fetch category {category_url}")
#         return []
    
#     soup = BeautifulSoup(resp.text, "html.parser")
#     links = set()
#     parsed_cat = urlparse(category_url)
#     cat_domain = parsed_cat.netloc.lower()

#     for a in soup.find_all("a", href=True):
#         abs_url = urljoin(category_url, a["href"])
#         parsed = urlparse(abs_url)
#         # Only consider links on the same domain.
#         if parsed.netloc.lower() != cat_domain:
#             continue

#         path = parsed.path.strip("/")
#         segments = [seg for seg in path.split("/") if seg]

#         if "pinchofyum.com" in cat_domain:
#             # Assume valid recipe URL has exactly one path segment.
#             if len(segments) == 1:
#                 links.add(abs_url)
#         elif "budgetbytes.com" in cat_domain:
#             exclude_keywords = ["category", "random", "about", "faq", "contact", "welcome", "index", "archive"]
#             if any(keyword in parsed.path.lower() for keyword in exclude_keywords):
#                 continue
#             if len(segments) == 1:
#                 links.add(abs_url)
#         elif "smittenkitchen.com" in cat_domain:
#             # Look for a date pattern (e.g., /2010/05/) in the path.
#             if re.search(r'^(\d{4})/(\d{2})/', parsed.path):
#                 links.add(abs_url)
#         elif "simplyrecipes.com" in cat_domain:
#             # Include if the path contains "recipes-" or "/recipes/"
#             if "recipes-" in parsed.path or "/recipes/" in parsed.path:
#                 links.add(abs_url)
#         elif "minimalistbaker.com" in cat_domain:
#             exclude_keywords = ["about", "shop", "resources", "contact", "privacy", "terms"]
#             if any(keyword in parsed.path.lower() for keyword in exclude_keywords):
#                 continue
#             # Assume a recipe URL is one with a slug (usually containing a hyphen)
#             if segments and "-" in segments[-1]:
#                 links.add(abs_url)
#         elif "halfbakedharvest.com" in cat_domain:
#             # Only include if "/recipes/" is present in the URL.
#             if "/recipes/" in abs_url:
#                 links.add(abs_url)
#         elif "joythebaker.com" in cat_domain:
#             # Look for a year/month pattern in the path.
#             if re.search(r'^/\d{4}/\d{2}/', parsed.path):
#                 links.add(abs_url)
#         elif "foodiecrush.com" in cat_domain:
#             # Include if the URL contains "/recipes/"
#             if "/recipes/" in abs_url:
#                 links.add(abs_url)
#         elif "kingarthurbaking.com" in cat_domain:
#             exclude_keywords = ["collections", "shop", "account", "baking-school", "learn", "videos", "contact", "privacy", "terms"]
#             if any(keyword in parsed.path.lower() for keyword in exclude_keywords):
#                 continue
#             # For King Arthur, include if the path has at least one hyphen (e.g., "holiday-cookies")
#             if "-" in parsed.path:
#                 links.add(abs_url)
#         elif "food52.com" in cat_domain:
#             if "/recipes/" in abs_url:
#                 links.add(abs_url)
#         else:
#             # Fallback rule.
#             if "/recipe/" in abs_url or "/recipes/" in abs_url:
#                 links.add(abs_url)
#     return list(links)

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python script.py <categories_csv_file>")
#         sys.exit(1)

#     # Read categories from CSV.
#     # CSV format: each row has at least two columns: category_name, category_url.
#     csv_filename = sys.argv[1]
#     categories = []  # list of tuples: (category_name, category_url)
#     with open(csv_filename, newline='', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:
#             if len(row) >= 2:
#                 cat_name = row[0].strip()
#                 cat_url = row[1].strip()
#                 if cat_url.startswith("http"):
#                     categories.append((cat_name, cat_url))

#     all_recipe_links = []
#     for cat_name, cat_url in categories:
#         print(f"Processing category: {cat_name} - {cat_url}")
#         recipe_links = get_recipe_links(cat_url)
#         print(f"Found {len(recipe_links)} recipe links in category {cat_name}")
#         # Extract category value from the URL (if available)
#         extracted_cat = extract_category_from_url(cat_url)
#         for link in recipe_links:
#             all_recipe_links.append({
#                 "category_name": cat_name,
#                 "category_url": cat_url,
#                 "category": extracted_cat,
#                 "recipe_url": link
#             })
#         time.sleep(2)  # be polite between category requests

#     # Write all collected recipe links to a CSV file.
#     output_csv = "recipe_links.csv"
#     with open(output_csv, "w", newline="", encoding="utf-8") as f:
#         fieldnames = ["category_name", "category_url", "category", "recipe_url"]
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in all_recipe_links:
#             writer.writerow(row)

#     print(f"Extracted recipe links saved to {output_csv}")




import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import time
import re

def extract_category_from_url(url):
    """
    Extracts a category value from a URL if it contains "/tag/".
    For example, from "https://www.budgetbytes.com/tag/celery/" it returns "celery".
    Otherwise, returns an empty string.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    if "/tag/" in path:
        parts = path.split("/tag/")
        if len(parts) > 1:
            return parts[1].split("/")[0]
    return ""

def get_recipe_links(category_url):
    """
    Fetch a category page and extract recipe links.
    
    Simplified rules:
      - Only consider links on the same domain as the category URL.
      - Exclude links that are exactly the category URL.
      - Include any link that contains "/recipe" (thus covering both "/recipe" and "/recipes")
        OR whose path matches a date pattern (e.g., /2020/09/), which is common for recipe URLs.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(category_url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error fetching category {category_url}: {e}")
        return []
    if resp.status_code != 200:
        print(f"Failed to fetch category {category_url} (status code: {resp.status_code})")
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    links = set()
    parsed_cat = urlparse(category_url)
    cat_domain = parsed_cat.netloc.lower()

    for a in soup.find_all("a", href=True):
        abs_url = urljoin(category_url, a["href"])
        parsed = urlparse(abs_url)
        # Only consider links on the same domain.
        if parsed.netloc.lower() != cat_domain:
            continue
        # Skip the category URL itself (ignoring trailing slash differences)
        if abs_url.rstrip("/") == category_url.rstrip("/"):
            continue
        # If the link includes "/recipe" (covers "/recipe" or "/recipes")
        if "/recipe" in abs_url:
            links.add(abs_url)
        else:
            # Alternatively, if the link matches a date pattern (e.g. /2020/09/), add it.
            if re.search(r'/\d{4}/\d{2}/', parsed.path):
                links.add(abs_url)
    return list(links)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <categories_csv_file>")
        sys.exit(1)

    # Read categories from CSV.
    # Expected CSV header: website, category_link
    csv_filename = sys.argv[1]
    categories = []  # List of tuples: (website, category_link)
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            website = row.get("website", "").strip()
            cat_link = row.get("category_link", "").strip()
            if cat_link.startswith("http"):
                categories.append((website, cat_link))

    all_recipe_links = []
    for website, cat_url in categories:
        print(f"Processing category: {website} - {cat_url}")
        recipe_links = get_recipe_links(cat_url)
        print(f"Found {len(recipe_links)} recipe links in category {website}")
        cat_value = extract_category_from_url(cat_url)
        for link in recipe_links:
            all_recipe_links.append({
                "website": website,
                "category_link": cat_url,
                "category": cat_value,
                "recipe_url": link
            })
        time.sleep(2)  # be polite between category requests

    output_csv = "recipe_links.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["website", "category_link", "category", "recipe_url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_recipe_links:
            writer.writerow(row)

    print(f"Extracted recipe links saved to {output_csv}")
