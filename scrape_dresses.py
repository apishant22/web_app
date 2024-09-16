import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import json

def scrape_meshki(url, keywords, color):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        product_cards = soup.find_all('div', class_='product-card')
        if not product_cards:
            print(f"Product cards not found for URL: {url}")
            return []

        dresses = []
        for product_card in product_cards:
            product_data = product_card.get('data-product-details')
            if not product_data:
                continue
            product_json = json.loads(product_data.replace('&quot;', '"'))

            title = product_json.get('title', 'No title')
            price_cents = product_json['selected_or_first_available_variant'].get('price', 0)
            price = f"£{price_cents / 100:.2f}"
            description = product_card.find('h4', class_='product-card__title').get_text(strip=True) if product_card.find('h4', class_='product-card__title') else 'No description'

            image_tag = product_card.find('img', class_='responsive-image__image')
            image = image_tag['src'] if image_tag and image_tag.has_attr('src') else 'No image'

            link_tag = product_card.find('a', href=True)  # Find the <a> tag with an href attribute
            relative_link = link_tag['href'] if link_tag else None
            link = f'https://www.meshki.co.uk{relative_link}' if relative_link else url  # Append the base URL

            dress_info = {
                "title": title,
                "price": price,
                "description": description,
                "image": image,
                "link": link
            }

            # Loosen matching criteria: At least one keyword should match
            text = f"{title.lower()} {description.lower()}"
            matched_keywords = [keyword for keyword in keywords if keyword in text]

            if matched_keywords and (color is None or color in text):
                dresses.append(dress_info)

        return dresses
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def build_little_mistress_url(keywords, color):
    base_url = "https://www.little-mistress.com/search?q="
    if color not in keywords:
        query_parts = [color] + keywords
    else:
        query_parts = keywords
    query_parts.append("dress")
    query = "+".join(query_parts)
    full_url = f"{base_url}{query}&options%5Bprefix%5D=last&type=product"
    return full_url

def scrape_little_mistress(url, keywords, color):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all product cards
        product_cards = soup.find_all('div', class_='product-index js-product-listing')
        if not product_cards:
            print(f"Product cards not found for URL: {url}")
            return []

        dresses = []
        for product_card in product_cards:
            # Extract product name (data-alpha) and price (data-price)
            title = product_card.get('data-alpha', 'No title')
            price_cents = product_card.get('data-price', 0)
            price = f"£{int(price_cents) / 100:.2f}"

            # Find product image by navigating through the nested divs
            prod_container = product_card.find('div', class_='prod-container')
            if prod_container:
                prod_image = prod_container.find('div', class_='prod-image image_natural')
                if prod_image:
                    reveal = prod_image.find('div', class_='reveal')
                    if reveal:
                        box_ratio = reveal.find('div', class_='box-ratio')
                        if box_ratio:
                            img_tag = box_ratio.find('img')  # Searching for any <img> tag inside box-ratio
                            if img_tag:
                                # Check if 'data-src' or 'data-original' exists
                                if img_tag.has_attr('data-src'):
                                    data_src = img_tag['data-src']
                                    # Replace {width} with 180 to get the desired image resolution
                                    image_url = data_src.replace("{width}", "180")
                                    image_url = f"https:{image_url}"
                                elif img_tag.has_attr('data-original'):
                                    image_url = f"https:{img_tag['data-original']}"
                                else:
                                    image_url = 'No image'
                            else:
                                image_url = 'No image'
                        else:
                            image_url = 'No image'
                    else:
                        image_url = 'No image'
                else:
                    image_url = 'No image'
            else:
                image_url = 'No image'

            # Find product link
            link_tag = prod_container.find('a', href=True)
            link = f"https://www.little-mistress.com{link_tag['href']}" if link_tag else url

            dress_info = {
                "title": title,
                "price": price,
                "description": title,  # Using title as description
                "image": image_url,  # Extracted image URL
                "link": link  # Product link
            }

            # Loosen matching criteria: At least one keyword should match
            text = f"{title.lower()}"
            matched_keywords = [keyword for keyword in keywords if keyword in text]

            if matched_keywords and (color is None or color in text):
                dresses.append(dress_info)

        # Check for pagination (if there's a "Next" button)
        next_page = soup.find('a', class_='next')  # Adjust the selector based on the website structure
        if next_page and 'href' in next_page.attrs:
            next_page_url = f"https://www.little-mistress.com{next_page['href']}"
            print(f"Found next page: {next_page_url}")
            next_dresses = scrape_little_mistress(next_page_url, keywords, color)
            dresses.extend(next_dresses)

        return dresses
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []



def google_search(query, num_results=50):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for g in soup.find_all('div', class_='tF2Cxc'):
        link = g.find('a')['href']
        links.append(link)
    return links

def extract_keywords(query):
    # Split the query into words and filter out stop words or irrelevant terms
    return [word.lower() for word in query.split()]

def extract_color(query):
    # List of common clothing colors
    colors = ["black", "white", "red", "blue", "green", "yellow", "pink", "purple", "orange", "brown", "gray", "grey", "navy", "beige", "gold", "silver", "ivory", "cream"]
    for word in query.lower().split():
        if word in colors:
            return word
    return None

def scrape_dress_info(url, keywords, color):
    if "meshki" in url:
        dresses = scrape_meshki(url, keywords, color)
        if dresses:
            print(f"Found {len(dresses)} dresses.")
            for dress in dresses:
                print(dress)
            return dresses
        else:
            print("No dresses found.")
            return None
    elif "little-mistress" in url:
        dresses = scrape_little_mistress(url, keywords, color)
        if dresses:
            print(f"Found {len(dresses)} dresses.")
            for dress in dresses:
                print(dress)
            return dresses
        else:
            print("No dresses found.")
            return None
    else:
        print(f"Website not supported for URL: {url}")
        return None


from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

def get_dress_data(user_query):
    keywords = extract_keywords(user_query)
    color = extract_color(user_query)

    shop_names = ["little mistress", "meshki"]
    dresses = []

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=0.1)  # Limiting search time

    def scrape_shop(shop):
        urls = []
        if shop == "little mistress":
            # Build Little Mistress search URL
            url = build_little_mistress_url(keywords, color)
            urls.append(url)
        else:
            # Build Meshki search using Google
            query = f"{user_query} {shop}"
            links = google_search(query)
            urls.extend(links)

        scraped_dresses = []
        for url in urls:
            if datetime.now() >= end_time:
                print("Time limit reached. Stopping the search and scraping process.")
                break
            try:
                print(f"Scraping {url} from {shop}")
                dress_infos = scrape_dress_info(url, keywords, color)
                if dress_infos:
                    scraped_dresses.extend(dress_infos)
            except Exception as e:
                print(f"Error scraping {url}: {e}")

        return scraped_dresses

    # Use ThreadPoolExecutor to scrape both shops concurrently
    with ThreadPoolExecutor(max_workers=len(shop_names)) as executor:
        futures = [executor.submit(scrape_shop, shop) for shop in shop_names]

        for future in futures:
            try:
                shop_dresses = future.result()
                if shop_dresses:
                    dresses.extend(shop_dresses)
            except Exception as e:
                print(f"Error in scraping process: {e}")

    return dresses

