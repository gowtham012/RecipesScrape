# #main code
# import requests
# from bs4 import BeautifulSoup
# import json
# import sys
# from urllib.parse import urlparse

# def clean_json_ld_text(text):
#     """Remove HTML comment markers and extra whitespace."""
#     if not text:
#         return text
#     text = text.strip()
#     if text.startswith("<!--"):
#         text = text.replace("<!--", "")
#     if text.endswith("-->"):
#         text = text.replace("-->", "")
#     return text.strip()

# def find_recipe_object(data):
#     """
#     Recursively search through data for an object that contains
#     both 'recipeIngredient' and 'recipeInstructions'.
#     """
#     if isinstance(data, dict):
#         if "recipeIngredient" in data and "recipeInstructions" in data:
#             return data
#         for key, value in data.items():
#             recipe = find_recipe_object(value)
#             if recipe:
#                 return recipe
#     elif isinstance(data, list):
#         for item in data:
#             recipe = find_recipe_object(item)
#             if recipe:
#                 return recipe
#     return None

# def extract_json_ld(soup):
#     """Extract JSON-LD data from the page and try to find the recipe object."""
#     scripts = soup.find_all("script", type="application/ld+json")
#     for script in scripts:
#         text = script.string
#         if not text:
#             continue
#         text = clean_json_ld_text(text)
#         try:
#             data = json.loads(text)
#         except Exception:
#             continue

#         # First try the conventional method: check for "@graph" with a Recipe.
#         if isinstance(data, dict) and "@graph" in data:
#             for item in data["@graph"]:
#                 if isinstance(item, dict) and item.get("@type") == "Recipe":
#                     return item

#         # Next, if data is a list, search for an object with "@type": "Recipe"
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict) and item.get("@type") == "Recipe":
#                     return item

#         # Lastly, do a recursive search for an object that contains recipe markers.
#         recipe_obj = find_recipe_object(data)
#         if recipe_obj:
#             return recipe_obj

#     return None

# def scrape_recipe(url):
#     result = {"url": url}
#     parsed = urlparse(url)
#     host = parsed.netloc.lower()
#     if host.startswith("www."):
#         host = host[4:]
#     result["host"] = host

#     # Supported domains (sample; add more as needed)
#     supported_domains = {
#         "allrecipes.com",
#         # ... add others from your list
#     }
#     result["wild_mode"] = False if host in supported_domains else True

#     headers = {"User-Agent": "Mozilla/5.0 (compatible; RecipeScraperBot/1.0)"}
#     resp = requests.get(url, headers=headers)
#     if resp.status_code != 200:
#         print(f"Failed to fetch {url}")
#         return None

#     soup = BeautifulSoup(resp.text, "html.parser")
#     json_ld = extract_json_ld(soup)

#     if json_ld:
#         result["title"] = json_ld.get("name", "")
#         author = json_ld.get("author", "")
#         if isinstance(author, dict):
#             result["author"] = author.get("name", "")
#         elif isinstance(author, list):
#             result["author"] = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in author)
#         else:
#             result["author"] = author

#         result["description"] = json_ld.get("description", "")
#         result["image"] = json_ld.get("image", "")
#         result["ingredients"] = json_ld.get("recipeIngredient", [])

#         instructions = json_ld.get("recipeInstructions", "")
#         if isinstance(instructions, list):
#             steps = []
#             for item in instructions:
#                 if isinstance(item, dict):
#                     steps.append(item.get("text", ""))
#                 else:
#                     steps.append(str(item))
#             result["instructions_list"] = steps
#             result["instructions"] = "\n".join(steps)
#         elif isinstance(instructions, str):
#             result["instructions_list"] = [instructions]
#             result["instructions"] = instructions
#         else:
#             result["instructions_list"] = []
#             result["instructions"] = ""

#         result["cook_time"] = json_ld.get("cookTime", "")
#         result["prep_time"] = json_ld.get("prepTime", "")
#         result["total_time"] = json_ld.get("totalTime", "")
#         result["servings"] = json_ld.get("recipeYield", "")
#         result["nutrients"] = json_ld.get("nutrition", {})

#         ratings = None
#         if "aggregateRating" in json_ld:
#             agg = json_ld["aggregateRating"]
#             if isinstance(agg, dict):
#                 ratings = agg.get("ratingValue", None)
#         result["ratings"] = ratings

#         result["category"] = json_ld.get("recipeCategory", "")
#         result["cuisine"] = json_ld.get("recipeCuisine", "")
#         result["language"] = "en"
#         result["site_name"] = host.capitalize()
#     else:
#         result["wild_mode"] = True
#         result["title"] = soup.title.string if soup.title else ""
#         # You can add more fallback extraction if needed.

#     return result

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python maincode.py <input_json_file>")
#         sys.exit(1)

#     with open(sys.argv[1], "r") as infile:
#         input_data = json.load(infile)

#     start_urls = input_data.get("start_urls", [])
#     output_data = []
#     for url in start_urls:
#         print(f"Scraping {url} ...")
#         recipe = scrape_recipe(url)
#         if recipe:
#             output_data.append(recipe)

#     print(json.dumps(output_data, indent=2))




#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import sys
import csv
from urllib.parse import urlparse

def clean_json_ld_text(text):
    """Remove HTML comment markers and extra whitespace."""
    if not text:
        return text
    text = text.strip()
    if text.startswith("<!--"):
        text = text.replace("<!--", "")
    if text.endswith("-->"):
        text = text.replace("-->", "")
    return text.strip()

def find_recipe_object(data):
    """
    Recursively search through data for an object that contains
    both 'recipeIngredient' and 'recipeInstructions'.
    """
    if isinstance(data, dict):
        if "recipeIngredient" in data and "recipeInstructions" in data:
            return data
        for key, value in data.items():
            recipe = find_recipe_object(value)
            if recipe:
                return recipe
    elif isinstance(data, list):
        for item in data:
            recipe = find_recipe_object(item)
            if recipe:
                return recipe
    return None

def extract_json_ld(soup):
    """Extract JSON-LD data from the page and try to find the recipe object."""
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        text = script.string
        if not text:
            continue
        text = clean_json_ld_text(text)
        try:
            data = json.loads(text)
        except Exception:
            continue

        # Try the conventional method: check for "@graph" with a Recipe.
        if isinstance(data, dict) and "@graph" in data:
            for item in data["@graph"]:
                if isinstance(item, dict) and item.get("@type") == "Recipe":
                    return item

        # If data is a list, search for a Recipe object.
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Recipe":
                    return item

        # Finally, perform a recursive search for an object that contains recipe markers.
        recipe_obj = find_recipe_object(data)
        if recipe_obj:
            return recipe_obj

    return None

def scrape_recipe(url):
    result = {"url": url}
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    result["host"] = host

    # Sample supported domains
    supported_domains = {
        "allrecipes.com",
        # add others as needed...
    }
    result["wild_mode"] = False if host in supported_domains else True

    headers = {"User-Agent": "Mozilla/5.0 (compatible; RecipeScraperBot/1.0)"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    json_ld = extract_json_ld(soup)

    if json_ld:
        result["title"] = json_ld.get("name", "")
        author = json_ld.get("author", "")
        if isinstance(author, dict):
            result["author"] = author.get("name", "")
        elif isinstance(author, list):
            result["author"] = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in author)
        else:
            result["author"] = author

        result["description"] = json_ld.get("description", "")
        result["image"] = json_ld.get("image", "")
        result["ingredients"] = json_ld.get("recipeIngredient", [])

        instructions = json_ld.get("recipeInstructions", "")
        if isinstance(instructions, list):
            steps = []
            for item in instructions:
                if isinstance(item, dict):
                    steps.append(item.get("text", ""))
                else:
                    steps.append(str(item))
            result["instructions_list"] = steps
            result["instructions"] = "\n".join(steps)
        elif isinstance(instructions, str):
            result["instructions_list"] = [instructions]
            result["instructions"] = instructions
        else:
            result["instructions_list"] = []
            result["instructions"] = ""

        result["cook_time"] = json_ld.get("cookTime", "")
        result["prep_time"] = json_ld.get("prepTime", "")
        result["total_time"] = json_ld.get("totalTime", "")
        result["servings"] = json_ld.get("recipeYield", "")
        result["nutrients"] = json_ld.get("nutrition", {})

        ratings = None
        if "aggregateRating" in json_ld:
            agg = json_ld["aggregateRating"]
            if isinstance(agg, dict):
                ratings = agg.get("ratingValue", None)
        result["ratings"] = ratings

        result["category"] = json_ld.get("recipeCategory", "")
        result["cuisine"] = json_ld.get("recipeCuisine", "")
        result["language"] = "en"
        result["site_name"] = host.capitalize()
    else:
        result["wild_mode"] = True
        result["title"] = soup.title.string if soup.title else ""
        # Additional fallback extraction could be added here.

    return result

def flatten_value(value):
    """Convert lists or dictionaries to a string suitable for CSV output."""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    elif isinstance(value, dict):
        return json.dumps(value)
    else:
        return value

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python maincode.py <input_json_file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as infile:
        input_data = json.load(infile)

    start_urls = input_data.get("start_urls", [])
    output_data = []
    for url in start_urls:
        print(f"Scraping {url} ...")
        recipe = scrape_recipe(url)
        if recipe:
            output_data.append(recipe)

    # Write output to CSV file.
    csv_file = "recipes.csv"
    # Define the CSV header fields in the desired order.
    fieldnames = [
        "url", "host", "wild_mode", "title", "author", "description", "image",
        "ingredients", "instructions", "instructions_list", "cook_time", "prep_time",
        "total_time", "servings", "nutrients", "ratings", "category", "cuisine",
        "language", "site_name"
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for recipe in output_data:
            # Flatten each field to ensure we store a string in the CSV.
            row = {key: flatten_value(recipe.get(key, "")) for key in fieldnames}
            writer.writerow(row)

    print(f"Scraped data saved to {csv_file}")
