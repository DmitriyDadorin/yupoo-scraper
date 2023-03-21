import requests
from bs4 import BeautifulSoup
import re
import csv

base_url = input("Enter base URL: ")

page_number = 1

items = []

while True:
    # Construct the URL for the current page
    url = f"{base_url}?page={page_number}"
    print(f"Scraping {url}")
    
    # Fetch the HTML content for the current page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all the divs with class "text_overflow album__title"
    divs = soup.find_all("div", {"class": "text_overflow album__title"})
    
    # If we didn't find any divs, then we've reached the end of the pages
    if not divs:
        break
    
    # Iterate over the divs and extract the information we want
    for div in divs:
        item = {}
        item["name"] = re.sub(r"[~.\U0001f525]", "", div.text.strip()) # Remove unwanted characters from name
        item["name"] = re.sub(r"\s*(?:￥|¥)\s*", "", item["name"]) # Remove CNY symbols from name
        picture_div = div.find_previous("div", {"class": "album__cover"})
        if picture_div:
            picture = picture_div.find("img").get("src")
            if picture:
                item["picture"] = "https:" + picture
            else:
                item["picture"] = ""
        else:
            item["picture"] = ""
        price = div.find_next("div", {"class": "album__price"})
        if price:
            price = price.text.strip()
            price = re.sub(r"\s", "", price)  # Remove any whitespace
            if "￥" in price or "¥" in price:
                price = float(price.replace("￥", "").replace("¥", "")) / 6.5  # Convert CNY to USD
            item["price"] = price
        else:
            item["price"] = ""
        link = div.find_previous("a").get("href")
        item["link"] = f"https://husky-reps.x.yupoo.com{link}" # Add base URL to link
        items.append(item)
    
    # Increment the page number for the next iteration
    page_number += 1

# Modify the items list to multiply the first number in the name by 0.145 and round to one decimal place
for item in items:
    first_num_match = re.search(r"^\d+", item["name"])
    if first_num_match:
        first_num = int(first_num_match.group())
        item["name"] = re.sub(r"^\d+", str(round(first_num * 0.145, 1)), item["name"])
        if "price" in item:
            del item["price"]  # Remove the price column from the item dictionary

# Update the fieldnames argument of the DictWriter object
fieldnames = ["name", "picture", "link"]

# Write the items to a CSV file
with open("items.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["name", "picture", "link", "price"])
    writer.writeheader()
    for item in items:
        if "price" in item:
            del item["price"]  # Remove the price column from the item dictionary
        writer.writerow(item)
