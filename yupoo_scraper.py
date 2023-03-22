import requests
from bs4 import BeautifulSoup
import re
import csv
from urllib.parse import urlparse

# base_url = input("Enter base URL: ")
base_url = "https://o832club.x.yupoo.com/categories/4113534"
parsed_url = urlparse(base_url)
url_append = f"{parsed_url.scheme}://{parsed_url.netloc}"
https_append = "https:"

page_number = 1

items = []

while True:
    
    # Construct the URL for the current page
    url = f"{base_url}?page={page_number}"
    
    # Fetch the HTML content for the current page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all the divs with class "text_overflow album__title"
    divs = soup.find_all("div", {"class": "text_overflow album__title"})

    # If we didn't find any divs, then we've reached the end of the pages
    if not divs:
        break
    
    print(f"Scraping {url}")
    
    # Iterate over the divs and extract the information we want
    for div in divs:
        item = {}
        div_text = div.text.strip()
        if div_text:
            item["name"] = re.sub(r"[~.\U0001f525]", "", div_text) # Remove unwanted characters from name
            item["name"] = re.sub(r"\s*(?:￥|¥)\s*", "", item["name"]) # Remove CNY symbols from name
            link = div.find_previous("a").get("href")
            item["link"] = f"{url_append}{link}" # Add URL to link
            
            # Find the corresponding img tag and add https: to its data-src attribute
            img_tag = div.find_next("img", {"class": "album__absolute album__img autocover"})
            if img_tag:
                item["picture"] = f"{https_append}{img_tag['data-src']}"

        items.append(item)
        

    # Increment the page number for the next iteration
    page_number += 1

# Modify the items list to multiply the first number in the name by 0.145 and round to one decimal place
for item in items:
    if "name" in item:
        first_num_match = re.search(r"^\d+", item["name"])
        if first_num_match:
            first_num = int(first_num_match.group())
            item["name"] = re.sub(r"^\d+", str(round(first_num * 0.145, 1)), item["name"])

# Update the fieldnames argument of the DictWriter object
fieldnames = ["name", "picture", "link"]

# Write the items to a CSV file
with open("items.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["name", "picture", "link"])
    writer.writeheader()
    for item in items:
        writer.writerow(item)
