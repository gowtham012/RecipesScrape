# import csv
# import json
# import sys

# def csv_to_json(input_csv, output_json):
#     urls = []
#     # Open CSV (assuming no header and that the 4th field contains the recipe URL)
#     with open(input_csv, newline='', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile)
#         for i, row in enumerate(reader):
#             # Ensure there are at least 4 columns
#             if len(row) >= 4:
#                 url = row[3].strip()
#                 if url.startswith("http"):
#                     urls.append(url)
#             else:
#                 print(f"Row {i} does not have enough fields: {row}")
#     data = {"start_urls": urls}
#     with open(output_json, "w", encoding="utf-8") as jsonfile:
#         json.dump(data, jsonfile, indent=2)
#     print(f"Converted {len(urls)} URLs into {output_json}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python csv_to_json.py <input_csv> <output_json>")
#         sys.exit(1)
#     input_csv = sys.argv[1]
#     output_json = sys.argv[2]
#     csv_to_json(input_csv, output_json)


import json

with open('input.json', 'r') as f:
    data = json.load(f)

data["start_urls"] = [
    url for url in data.get("start_urls", [])
    if "replytocom" not in url and "#comment" not in url
]

with open('output.json', 'w') as f:
    json.dump(data, f, indent=2)
